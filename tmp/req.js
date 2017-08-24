var page = require('webpage').create(),
    system = require('system'),
    address, porxy;
var settings = {
    'proxy': '',
};    
var UA_list = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X; zh-CN) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/13D15 UCBrowser/10.9.15.793 Mobile',
    'Mozilla/5.0 (iPhone 6p; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/6.0 MQQBrowser/6.7 Mobile/13D15 Safari/8536.25 MttCustomUA/2',
    'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; SM-J3109 Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 Chrome/37.0.0.0 MQQBrowser/6.6 Mobile Safari/537.36',
    ]
    
address = system.args[1];
//settings['proxy'] = system.args[2]
 
//init and settings
page.settings.resourceTimeout = 30000;
page.settings.XSSAuditingEnabled = true;
page.settings.userAgent = UA_list[Math.floor(Math.random()*UA_list.length)];
page.customHeaders = {
    "Connection" : "keep-alive",
    "Cache-Control" : "max-age=0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
};

//page.open(address, settings);
page.open(address);
//加载页面完毕运行
page.onLoadFinished = function(status) {
    console.log('Status:' + status);
    //console.log('Content:' + page.content);
    console.log('URL:' + page.url);
    console.log('Title:' + page.title);
    var time = new Date()
    console.log('-----' + time + '--------')
    phantom.exit();
};