# dev_web

> A Vue.js project

## Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```

For a detailed explanation on how things work, check out the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).

## Notes

### A process to init a project 

```
vue create .
vue init webpack .
npm install element-ui <with args>
npm run dev 
```

If you meet the error with webpack-cli versions, you can try the command `npm install webpack-cli --legacy-peer-deps`. Refer to [here](https://blog.csdn.net/devcloud/article/details/124469666) (So complicated!)

### Some info about ssl verify 

<pre>
python最新版的requests不支持屏蔽ssl校验，需要先对requests进行版本降级，然后通过CURL_CA_BUNDLE关掉校验

1）首先降级requests版本
pip uninstall requests

2）安装降版本的requests包
pip install requests==2.27.1

3）暴力关掉SSL验证
建议：在代码头部配置该环境变量，建议每次跑代码之前运行一次即可
import os
import urllib3

os.environ['CURL_CA_BUNDLE'] = ''    # 关闭SSL证书验证
urllib3.disable_warnings()   # 关闭告警
</pre>
