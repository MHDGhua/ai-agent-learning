# Cloudflare 解析设置

你当前的域名权威 DNS 在 Cloudflare：

- `grace.ns.cloudflare.com`
- `felicity.ns.cloudflare.com`

这意味着阿里云域名后台里看到的解析记录不会真正生效，必须去 Cloudflare 后台改。

## 你当前需要改成这样

### 1. 根域名

- 类型：`A`
- 名称：`@`
- 内容：`38.76.160.95`
- 代理状态：先开 `DNS only` 灰云，部署成功后可切橙云

### 2. www 子域名

- 类型：`CNAME`
- 名称：`www`
- 内容：`tinko.xin`
- 代理状态：先开 `DNS only`

## 为什么先灰云

第一次部署自动 HTTPS 时，先用灰云更容易让证书顺利签发。等站点通了，再切到橙云。

## 改完怎么检查

在本机执行：

```bash
nslookup tinko.xin
nslookup www.tinko.xin
```

根域名应最终指向你的服务器 `38.76.160.95`。

## 部署完成后

如果你要继续使用 Cloudflare 代理：

1. 把 `@` 和 `www` 切成橙云
2. 进入 Cloudflare 的 `SSL/TLS`
3. 选择 `Full` 或 `Full (strict)`
