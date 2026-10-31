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
    body += text(72,350,'AI Coding',118,'#edf6f5','font-weight="650"')+text(72,485,'Agent',118,'#edf6f5','font-weight="650"')
    body += text(80,640,'设计与实现',105,'#65dfc9','font-weight="500" letter-spacing="14"')
    body += text(84,735,'架构、核心机制与关键工程细节',34,'#c1d0d5')
    coords=[(100,960,'MODEL'),(670,960,'TOOLS'),(100,1270,'CONTEXT'),(670,1270,'STATE')]
    body += '<path d="M340 1030 H670 M790 1100 V1270 M670 1340 H340 M220 1270 V1100" stroke="#65dfc9" stroke-width="5" fill="none"/>'
    for x,y,label in coords:
        body += f'<rect x="{x}" y="{y}" width="340" height="140" rx="8" fill="#102a37" stroke="#65dfc9" stroke-width="2"/>'+text(x+34,y+85,label,36,'#edf6f5','class="mono"')
    body += '<circle cx="840" cy="1030" r="10" fill="#f5b571"/>'
    body += text(80,1530,'CODEX  /  DEEPSEEK HARNESS',28,'#c6d7da','class="mono"')
    body += text(80,1580,'PI  /  CLAUDE CODE',28,'#c6d7da','class="mono"')
    body += text(80,1720,'Aias00',28,'#edf6f5')+text(1120,1720,'02  /  2026',24,'#8faab6','text-anchor="end" class="mono"')
    (OUT/'cover.svg').write_text(svg(1200,1800,'AI Coding Agent 设计与实现封面',body,True))
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
    body=DEFS+text(45,55,'控制面拥有决策，执行面产生效果，存储保存事实',28)
    body+=box(45,100,245,80,'CLI / IDE / Web')+box(385,100,260,80,'Session Actor')+box(745,100,230,80,'Model Adapter')
    body+=arrow(290,140,385,140)+arrow(645,140,745,140)
    body+=box(45,270,245,80,'Policy / Grant')+box(385,270,260,80,'Scheduler')+box(745,270,230,80,'Executor')
    body+=arrow(515,180,515,270)+arrow(290,310,385,310)+arrow(645,310,745,310)
    body+=box(280,440,480,80,'Event Store + Artifact Store','#d9efea')
    body+=arrow(865,350,760,440)+arrow(515,350,515,440)+arrow(280,480,170,180)
    body+=text(45,585,'命令提交与事实订阅分开；工具结果通过状态所有者进入下一请求。',21,'#4c6873')
    (OUT/'architecture.svg').write_text(svg(1020,630,'Coding Agent 控制面、执行面与事实存储架构',body))
    body=DEFS+text(45,55,'回合状态与关键交接',30)
    labels=[(45,110,'idle'),(385,110,'preparing'),(725,110,'generating'),(725,290,'executing'),(385,290,'settling'),(45,290,'terminal')]
    for x,y,label in labels: body+=box(x,y,250,80,label)
    body+=arrow(295,150,385,150)+arrow(635,150,725,150)+arrow(850,190,850,290)+arrow(725,330,635,330)+arrow(385,330,295,330)
    body+='<path d="M510 290 V190" fill="none" stroke="#278c91" stroke-width="3" marker-end="url(#arrow)"/>'
    body+=text(45,450,'取消：停止新派发 → 收集已开始结果 → 保留未知效果 → 终结',22,'#4c6873')
    body+=text(45,500,'awaiting_approval 是持久暂停；terminal 不再启动隐含工作。',22,'#4c6873')
    (OUT/'state-machine.svg').write_text(svg(1020,550,'回合状态机示意图',body))
    body=DEFS+text(45,55,'授权绑定实际行动，执行前再次复核',30)
    for x,label in [(45,'规范化参数'),(385,'行动与权限摘要'),(725,'Grant')]: body+=box(x,110,250,80,label,size=22)
    body+=arrow(295,150,385,150)+arrow(635,150,725,150)
    body+=box(385,300,590,90,'参数 / 目标 / 策略 / 期限全部匹配','#d9efea',size=23)
    body+=arrow(850,190,850,300)+box(45,300,250,90,'资源就绪')+arrow(295,345,385,345)
    body+=text(45,465,'参数或权限升级发生变化：旧 Grant 失效，重新判断授权。',23,'#4c6873')
    (OUT/'authorization.svg').write_text(svg(1020,530,'授权规范化、摘要绑定与执行前复核',body))
    print('Created original cover and six architecture diagrams.')

if __name__ == '__main__': main()
