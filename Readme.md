# 服务启动命令
python api_service.py （开启gradio前端服务）
python flask_service.py （开启代理，实现在线图片下载和转发成外网可访问的url）

# 代理
对应到config的NGINX
## ngrok
临时url："https://6873-58-250-250-208.ngrok-free.app" 
启动命令：./ngrok http 8889
token配置命令：ngrok config add-authtoken 2reuMuQbLzXF20Zt1wYxKqXc48Y_2dYPUFdQK1FtDtbdEJqXw
参考文档：https://dashboard.ngrok.com/get-started/your-authtoken
问题：有visit website页面；
## natapp（当前使用）
临时url："http://z5hv9b.natappfree.cc"
启动命令：
cd /Users/admin/program/softwares/
./natapp -authtoken=416b18891cccda9c

参考文档：https://natapp.cn/tunnel/lists
## sunny-ngrok
临时url："http://momo.free.idcfengye.com"  
启动命令：./sunny --server=free.idcfengye.com:4443 --key=172844443208
参考文档：https://www.ngrok.cc/user.html
问题：太慢了，经常崩
