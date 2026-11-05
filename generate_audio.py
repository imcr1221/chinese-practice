import asyncio, hashlib, json, os, re, glob
import edge_tts

VOICE = "zh-CN-XiaoyiNeural"
RATE  = "-25%"
PITCH = "+8Hz"
OUT   = "audio"

os.makedirs(OUT, exist_ok=True)

def extract_texts_from_html(filepath):
    texts = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        
        # 抓取所有的引号内文本
        matches = re.findall(r'[\'"`](.*?)[\'"`]', html, re.DOTALL)
        for content in matches:
            content = content.strip()
            # 只保留包含中文的，长度小于200的，避免抓取代码
            if re.search(r'[\u4e00-\u9fa5]', content) and len(content) < 200:
                texts.add(content)
                
        # 抓取课文 story 数组
        story_match = re.search(r'const story=\[(.*?)\];', html, re.DOTALL)
        if story_match:
            parts = re.findall(r'[\'"`](.*?)[\'"`]', story_match.group(1), re.DOTALL)
            full_story = "".join([p.replace('\\n', '').strip() for p in parts])
            if full_story:
                texts.add(full_story)
    except Exception as e:
        print(f"读取 {filepath} 失败: {e}")
    return texts

async def main():
    all_texts = set()
    
    # 【关键】递归搜索所有的 html 文件（包括 texts/ 和 grammar/ 里的）
    html_files = glob.glob('**/*.html', recursive=True)
    for filepath in html_files:
        if 'index.html' in filepath: continue # 跳过目录索引页
        all_texts.update(extract_texts_from_html(filepath))

    print(f"全站共扫描到 {len(all_texts)} 条不重复的中文文本。")

    manifest = {}
    for text in all_texts:
        name = hashlib.md5(text.encode("utf-8")).hexdigest()[:12] + ".mp3"
        path = os.path.join(OUT, name)
        manifest[text] = f"audio/{name}"
        
        if os.path.exists(path):
            continue
        try:
            c = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
            await c.save(path)
            print("生成音频:", text[:15] + ("..." if len(text)>15 else ""))
        except Exception as e:
            print("失败:", text, e)

    with open(os.path.join(OUT, "tts-manifest.js"), "w", encoding="utf-8") as f:
        f.write("window.TTS_AUDIO=" + json.dumps(manifest, ensure_ascii=False) + ";\n")
    print("全站 manifest 已写入 audio/tts-manifest.js")

asyncio.run(main())
