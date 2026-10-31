#!/usr/bin/env python3
"""Create original vector artwork; cover PNG is rendered by a browser once."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'

def svg(width, height, title, body, dark=False):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><style>text{{font-family:"PingFang SC","Microsoft YaHei",sans-serif}}.mono{{font-family:monospace}}</style><rect width="100%" height="100%" fill="{'#0e202c' if dark else '#f1f6f4'}"/>{body}</svg>'''

def text(x, y, value, size=24, fill='#203947', extra=''):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" {extra}>{escape(value)}</text>'

def box(x,y,w,h,label,fill='#ffffff',color='#173d48',size=23):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="#b4d3d0"/>'+text(x+w/2,y+h/2+8,label,size,color,'text-anchor="middle"')

def arrow(x1,y1,x2,y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#278c91" stroke-width="3" marker-end="url(#arrow)"/>'

DEFS='<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#278c91"/></marker></defs>'

def main():
    OUT.mkdir(exist_ok=True)
    body = ''.join(f'<path d="M{x} 780 V1660" stroke="#244250" stroke-width="1"/>' for x in range(100,1150,70))
    body += ''.join(f'<path d="M80 {y} H1120" stroke="#244250" stroke-width="1"/>' for y in range(810,1690,70))
    body += '<rect x="80" y="110" width="54" height="8" fill="#65dfc9"/>'
    body += text(80,180,'SOURCE CODE / RUNTIME / ENGINEERING',25,'#8faab6','letter-spacing="3"')
    body += text(72,350,'Coding',118,'#edf6f5','font-weight="650"')+text(72,485,'Agent',118,'#edf6f5','font-weight="650"')
    body += text(80,640,'工程剖析',105,'#65dfc9','font-weight="500" letter-spacing="14"')
    body += text(84,735,'从四套实现，读懂智能体运行时',34,'#c1d0d5')
    coords=[(100,960,'MODEL'),(670,960,'TOOLS'),(100,1270,'CONTEXT'),(670,1270,'STATE')]
    body += '<path d="M340 1030 H670 M790 1100 V1270 M670 1340 H340 M220 1270 V1100" stroke="#65dfc9" stroke-width="5" fill="none"/>'
    for x,y,label in coords:
        body += f'<rect x="{x}" y="{y}" width="340" height="140" rx="8" fill="#102a37" stroke="#65dfc9" stroke-width="2"/>'+text(x+34,y+85,label,36,'#edf6f5','class="mono"')
    body += '<circle cx="840" cy="1030" r="10" fill="#f5b571"/>'
    body += text(80,1530,'CODEX  /  DEEPSEEK HARNESS',28,'#c6d7da','class="mono"')
    body += text(80,1580,'PI  /  CLAUDE CODE',28,'#c6d7da','class="mono"')
    body += text(80,1720,'Aias00',28,'#edf6f5')+text(1120,1720,'01  /  2026',24,'#8faab6','text-anchor="end" class="mono"')
    (OUT/'cover.svg').write_text(svg(1200,1800,'Coding Agent 工程剖析封面',body,True))
    (OUT/'favicon.svg').write_text(svg(64,64,'Coding Agent', '<path d="M18 20 L8 32 L18 44 M46 20 L56 32 L46 44 M37 15 L27 49" stroke="#65dfc9" stroke-width="5" fill="none"/>',True))
    body=DEFS+text(45,55,'一次任务中的六个责任',30)
    labels=['接纳输入','形成请求','模型生成','提交与验证','工具副作用','执行决策']
    for i,label in enumerate(labels):
        x=45+(i%3)*325;y=100+(i//3)*150
        body+=box(x,y,270,80,label)
    body+=arrow(315,140,370,140)+arrow(640,140,695,140)+arrow(830,180,830,250)+arrow(695,290,640,290)+arrow(370,290,315,290)
    body+=text(45,400,'循环依据结果继续；完成依据验证，而非助手自述。',22,'#4c6873')
    (OUT/'loop.svg').write_text(svg(1020,450,'任务执行循环及六项责任',body))
    body=DEFS+text(45,55,'执行发生，与结果已知，是两件事',30)
    for i,(label,fill) in enumerate([('意图已记录','#fff'),('工具已派发','#fff'),('副作用发生','#fff0d9'),('结果已提交','#fff')]):
        x=40+i*247;body+=box(x,115,210,90,label,fill,size=21)
        if i<3:body+=arrow(x+210,160,x+247,160)
    body+='<rect x="535" y="240" width="420" height="105" rx="12" fill="#ffedd5" stroke="#dba653"/>'
    body+=text(558,280,'在这里崩溃：结果未知',24,'#81571b')+text(558,319,'先核对现实状态，再决定是否重试',20,'#81571b')
    body+=arrow(650,210,650,240)+text(45,400,'持久日志 ≠ 任意外部副作用的原子事务',23,'#4c6873')
    (OUT/'unknown-window.svg').write_text(svg(1040,450,'外部副作用与结果提交之间的未知窗口',body))
    body=DEFS+text(45,55,'并行执行，有序提交',30)
    for i,label in enumerate(['A：读取实现','B：读取测试','C：独占编辑']):
        body+=text(45,140+i*90,label,23)
    body+='<rect x="250" y="110" width="330" height="48" rx="5" fill="#95d4ca"/><rect x="250" y="200" width="135" height="48" rx="5" fill="#95d4ca"/><rect x="640" y="290" width="240" height="48" rx="5" fill="#e6bd7e"/>'
    body+=text(430,145,'执行',21)+text(268,235,'执行',21)
    body+='<path d="M600 90 V355" stroke="#278c91" stroke-width="2" stroke-dasharray="7 5"/>'
    body+=text(615,85,'屏障',20,'#278c91')+text(410,235,'等待 A 后提交 B',20,'#4c6873')+text(45,410,'示意图：具体调度、限流与取消语义以各项目为准。',22,'#4c6873')
    (OUT/'parallel.svg').write_text(svg(1020,460,'并行读取和独占编辑的示意时间线',body))
    print('Created original cover and three architecture diagrams.')

if __name__ == '__main__': main()
