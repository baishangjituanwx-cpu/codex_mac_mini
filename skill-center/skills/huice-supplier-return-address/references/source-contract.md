# 慧策供应商售后地址接口契约

## 已确认页面与接口

- 页面路径：慧策“分析 → 供应商管理 → 供销商售后退货地址”。
- 供销商列表读取：`POST /scmapi/api/admin/distributor/my/supplier`。
- 当前已确认的供应商地址字段：`saleReturnPlaces[]`。
- 供应商主键字段：`shopId`；辅助稳定字段：`supCompanyName`、`nickNo`。
- 地址字段：`provinceName`、`cityName`、`regionName`、`detailAddress`；`fullAddress` 只作摘要，不能代替详细地址。
- 页面列名对应说明字段：`saleReturnAddress`；“供应商未维护”或空地址不能放行。
- 售后处理状态字段：`afterSeal`；它不能代替地址完整性判断。

## 读取要求

1. 使用共享慧策 HTTP 客户端读取已合作供应商全量分页，不通过浏览器点击业务按钮。
2. 用商品当前的 `supplierShopId` 与供应商 `shopId` 精确匹配；匹配不到或匹配多条时不使用地址。
3. 逐条验证省、市、区/县、详细地址；只返回城市摘要的 `fullAddress` 不算完整地址。
4. `saleReturnPlaces` 记录不得输出联系人手机号；业务台账只保存脱敏电话或地址来源状态。
5. 页面字段或接口契约变化时，先重新只读抓取网络请求并更新本文件，再恢复候选扫描。

## Windows 读取约定

Windows 继续使用同一个共享 HTTP 客户端和本仓库已有的 PowerShell/Node 启动入口（如调用方技能提供），不要复制 Mac 的 `/Volumes/...` 路径，也不要新建临时业务包装器。共享目录改用带引号的 UNC 或映射盘路径，证据文件使用带引号的 `C:/Users/<name>/...` 路径；认证信息只存在当前 PowerShell 会话，不使用 `setx`、注册表持久化或跟踪文件。

## 结果状态

扫描结果应写中文业务说明，例如“慧策供销商售后退货地址已匹配”“供应商未维护”“供应商地址匹配不唯一”“供应商身份无法确认”。机器状态码只放在专用代码字段，不能直接占用成本、库存或人工核对列。
