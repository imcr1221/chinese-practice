// js/tts.js
(function() {
    // 动态引入生成的音频清单
    const isSubfolder = window.location.pathname.includes('/texts/') || window.location.pathname.includes('/grammar/');
    const script = document.createElement('script');
    script.src = isSubfolder ? '../audio/tts-manifest.js' : './audio/tts-manifest.js';
    document.head.appendChild(script);

    let currentAudio = null;
    
    // 挂载全局 speak 函数
    window.speak = function(text) {
        let textKey = text.trim();
        
        if (window.TTS_AUDIO && window.TTS_AUDIO[textKey]) {
            if ('speechSynthesis' in window) speechSynthesis.cancel();
            if (currentAudio) { currentAudio.pause(); currentAudio.currentTime = 0; }
            
            let audioPath = window.TTS_AUDIO[textKey];
            // 如果在子文件夹，需要加上 ../
            if (isSubfolder) audioPath = '../' + audioPath;
            
            currentAudio = new Audio(audioPath);
            currentAudio.play();
            return;
        }
        
        // 降级用系统语音
        if (!('speechSynthesis' in window)) { return; }
        speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(textKey);
        u.lang = 'zh-CN'; u.rate = 0.83;
        const v = speechSynthesis.getVoices().find(x => x.lang.toLowerCase().startsWith('zh'));
        if (v) u.voice = v;
        speechSynthesis.speak(u);
    };
})();
