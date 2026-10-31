#!/usr/bin/env python3
"""Validate publication structure and links, independently of optional browser QA."""
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
NS = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container', 'o': 'http://www.idpf.org/2007/opf', 'd': 'http://purl.org/dc/elements/1.1/'}

class Document(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.ids = set()
        self.refs = []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids: raise ValueError('Duplicate HTML id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        for attribute in ['href', 'src']:
            if attribute in attrs: self.refs.append(attrs[attribute])

def main():
    snapshot = json.loads((ROOT / 'research/sources.json').read_text())
    ids = {r['id'] for r in snapshot['files']}
    referenced = set()
    chapter_paths = sorted((ROOT / 'chapters').glob('*.md'))
    for path in chapter_paths:
        body = path.read_text()
        if not body.startswith('# '): raise ValueError(f'Missing chapter title: {path}')
        referenced.update(re.findall(r'〔([CDPA]\d{2})〕', body))
        if re.search(r'\b(TODO|FIXME|TBD)\b', body): raise ValueError(f'Unfinished prose: {path}')
    if referenced - ids: raise ValueError(f'Unknown source references: {referenced - ids}')
    for row in snapshot['files']:
        if not re.fullmatch('[0-9a-f]{64}', row['sha256']): raise ValueError('Invalid source hash')
        if row.get('matches_embedded_source') is False: raise ValueError('Source map mismatch')
    site = ROOT / 'site'
    pages = {p.relative_to(site).as_posix(): Document(p.read_text()) for p in site.glob('*.html')}
    checked_html = 0
    for name, doc in pages.items():
        for ref in doc.refs:
            parts = urlsplit(ref)
            if parts.scheme or parts.netloc: continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parts.path))) if parts.path else name
            if not (site / target).is_file(): raise ValueError(f'Broken site link: {name} -> {ref}')
            if parts.fragment and target in pages and unquote(parts.fragment) not in pages[target].ids:
                raise ValueError(f'Broken site anchor: {name} -> {ref}')
            checked_html += 1
    epub = ROOT / 'dist/coding-agent-engineering.epub'
    with zipfile.ZipFile(epub) as archive:
        entries = archive.infolist()
        if entries[0].filename != 'mimetype' or entries[0].compress_type != zipfile.ZIP_STORED:
            raise ValueError('EPUB mimetype must be first and uncompressed')
        if archive.read('mimetype') != b'application/epub+zip': raise ValueError('Wrong EPUB mimetype')
        names = set(archive.namelist())
        xml = {n: ET.fromstring(archive.read(n)) for n in names if n.endswith(('.xml', '.xhtml', '.opf', '.ncx', '.svg'))}
        rootfile = xml['META-INF/container.xml'].find('c:rootfiles/c:rootfile', NS).attrib['full-path']
        opf = xml[rootfile]
        manifest = {item.attrib['id']: item.attrib for item in opf.findall('o:manifest/o:item', NS)}
        for item in manifest.values():
            href = posixpath.normpath(posixpath.join(posixpath.dirname(rootfile), unquote(item['href'])))
            if href not in names: raise ValueError('Missing EPUB manifest file: ' + href)
        spine = opf.findall('o:spine/o:itemref', NS)
        for item in spine:
            if item.attrib['idref'] not in manifest: raise ValueError('Missing EPUB spine item')
        if opf.find('o:metadata/d:language', NS).text != 'zh-CN': raise ValueError('Incorrect book language')
        xml_ids = {name: {node.attrib['id'] for node in tree.iter() if 'id' in node.attrib} for name, tree in xml.items()}
        checked_epub = 0
        for name, tree in xml.items():
            for node in tree.iter():
                for attribute in ['href', 'src']:
                    ref = node.attrib.get(attribute)
                    if not ref: continue
                    parts = urlsplit(ref)
                    if parts.scheme or parts.netloc: continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parts.path))) if parts.path else name
                    if target not in names: raise ValueError(f'Broken EPUB resource: {name} -> {ref}')
                    if parts.fragment and target in xml_ids and unquote(parts.fragment) not in xml_ids[target]:
                        raise ValueError(f'Broken EPUB anchor: {name} -> {ref}')
                    checked_epub += 1
    if hashlib.sha256(epub.read_bytes()).hexdigest() != hashlib.sha256((site / 'downloads' / epub.name).read_bytes()).hexdigest():
        raise ValueError('Website and EPUB download differ')
    report = {'structural_checks': 'passed', 'epub_sha256': hashlib.sha256(epub.read_bytes()).hexdigest(), 'chapter_documents': len(chapter_paths), 'html_pages': len(pages),
        'html_internal_links_checked': checked_html, 'epub_resources': len(names), 'epub_spine_items': len(spine),
        'epub_internal_links_checked': checked_epub, 'source_records': len(ids), 'source_ids_cited': len(referenced),
        'extracted_implementation_files_matched_to_map': sum(r.get('matches_embedded_source', False) for r in snapshot['files']),
        'scope': 'Publication structure and internal references; upstream execution and real-model performance are not tested.'}
    for destination in [ROOT / 'dist/validation.json', site / 'validation.json']:
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
