# 厦门大学自动打卡脚本
每日9时 n 分打卡，n 取决于运行脚本时的分钟数

可以放在服务器上自动运行，只需要在 /etc/profiles.d/ 目录下新建 health.sh，并输入

    python3 /path/to/your/script/parse.py
这样就可以开机自动运行了

### 需要安装的pip库：
* httpx
* lxml
* pyexecjs
* ujson
