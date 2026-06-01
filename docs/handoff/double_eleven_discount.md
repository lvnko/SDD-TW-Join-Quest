# 功能交接文件：雙十一大量購買折扣（DoubleElevenDiscount）

## 1. Feature 概述

**業務目的：**
在雙十一活動期間，針對訂單中每種商品的購買數量獨立計算折扣——每購買同一種商品滿 10 件，即可享有該 10 件組合 8 折的優惠；不足 10 件的餘數則以原價計算。不同商品之間的數量不合併計算。

**對應 spec 檔案：**
- 原始規格：`docs/specs/campaign.feature`
- 實際執行的 feature 檔：`features/campaign.feature`（標記 `@double_eleven`）

---

## 2. 實作架構摘要

### 核心類別

| 類別 | 檔案 | 職責 |
|------|------|------|
| `DoubleElevenDiscount` | `src/promotions.py` | 促銷策略：按商品逐一計算每滿 10 件的 8 折折扣，僅修改折扣數字，不變更商品明細清單 |
| `OrderService` | `src/order_service.py` | 結帳服務，迭代所有注入的促銷策略，依序呼叫 `apply()`，**無需修改即可支援新促銷** |
| `OrderItem` | `src/entities.py` | 訂單明細值物件，持有 `product`（含 `unit_price`）與 `quantity` |
| `Product` | `src/entities.py` | 商品值物件，持有 `name`、`unit_price`、`category` |
| `Order` | `src/entities.py` | 結帳結果值物件，持有 `items`、`original_amount`、`discount`、`total_amount` |

### 類別依賴關係

```
OrderService
  └─ 注入 DoubleElevenDiscount（促銷策略，duck typing）
       └─ 讀取 OrderItem.quantity
       └─ 讀取 OrderItem.product.unit_price
```

`DoubleElevenDiscount` 不繼承任何基底類別，僅需實作與其他促銷策略相同的方法簽名（duck typing）：

```python
def apply(self, items: list[OrderItem], original_amount: float, current_discount: float) -> tuple[float, list[OrderItem]]:
    ...
```

### 各檔案路徑與用途

| 路徑 | 用途 |
|------|------|
| `src/promotions.py` | 所有促銷策略類別（含 `DoubleElevenDiscount`） |
| `src/order_service.py` | 結帳服務，促銷迭代邏輯 |
| `src/entities.py` | 資料模型：`Product`、`OrderItem`、`Order` |
| `features/campaign.feature` | 雙十一折扣的 BDD feature 檔 |
| `features/steps/campaign_steps.py` | 雙十一折扣對應的 Behave step definitions |
| `features/order.feature` | 其他既有促銷的 BDD feature 檔（回歸測試用） |
| `features/steps/order_steps.py` | 既有促銷的 step definitions |
| `features/environment.py` | Behave 環境設定（`before_scenario` hook，初始化 `context.promotions`） |

---

## 3. 商業邏輯重點

### 已實作的折扣規則

- **計算單位為「商品」**：折扣以每種商品的 `quantity` 獨立計算，不同商品之間的數量**不合併**。
- **門檻為每滿 10 件**：對每種商品計算完整組數 `complete_groups = quantity // 10`。
- **折扣幅度為 8 折**：每個完整組的折扣金額為 `10 × unit_price × 0.2`（即原價的 20%）。
- **餘數不享折扣**：`quantity % 10` 的餘數件數以原價計算，不套入任何折扣。
- **折扣金額累加**：回傳 `current_discount + added_discount`，與其他促銷策略的折扣可疊加。
- **不修改商品明細清單**：`apply()` 回傳的 `items` 與傳入的相同，不新增或移除明細項目。

### 折扣計算公式

```
added_discount = Σ (item.quantity // 10) × 10 × item.product.unit_price × 0.2
total_amount   = original_amount - (current_discount + added_discount)
```

### 邊界條件與容易誤解的行為

| 情境 | 正確行為 | 常見誤解 |
|------|----------|----------|
| 同一訂單中有 10 種不同商品各 1 件 | 無折扣（每種商品各自不足 10 件） | 誤以為「合計 10 件」即可觸發折扣 |
| 購買剛好 10 件同種商品 | 觸發折扣，`10 // 10 = 1` 組 | 誤以為需要「超過」10 件 |
| 購買 27 件同種商品 | 2 組享折扣，7 件原價（`27 // 10 = 2`） | 誤以為 20 件後全部適用折扣 |
| 混合商品（如 12 件襪子 + 1 件上衣） | 折扣僅套用於襪子（`12 // 10 = 1` 組），上衣原價 | 誤以為不同商品數量可合併 |

---

## 4. 測試覆蓋摘要

### Scenario 清單（`features/campaign.feature`）

| Scenario 名稱 | 測試核心行為 | 結果 |
|---------------|-------------|------|
| 購買同一種商品少於 10 件——不套用任何折扣 | 未達門檻時折扣為 0，total = 原價 | ✅ pass |
| 購買超過 10 件——折扣適用於每滿 10 件的完整組 | 1 個完整組享折扣，餘數原價 | ✅ pass |
| 購買超過 20 件——折扣分別適用於每個獨立的滿 10 件組 | 2 個完整組各別計算折扣 | ✅ pass |
| 購買 10 件不同商品——不套用任何折扣 | 數量不跨商品合併，各自不足 10 件 | ✅ pass |
| 購買同一種商品剛好 10 件 | 邊界值：剛好 10 件即觸發折扣 | ✅ pass |
| 購買 12 件襪子與 1 件上衣——折扣僅適用於襪子 | 不同商品折扣計算互不干擾 | ✅ pass |

### 完整測試套件執行結果

執行指令：`.venv/bin/behave`（含 `order.feature` 與 `campaign.feature`）

```
2 features passed, 0 failed, 0 skipped
12 scenarios passed, 0 failed, 0 skipped
43 steps passed, 0 failed, 0 skipped
```

---

## 5. 已知限制與假設

### 設計假設

- **商品識別以 `OrderItem` 物件為單位**：`DoubleElevenDiscount.apply()` 逐一迭代傳入的 `items` 清單，並以每個 `OrderItem` 作為獨立的折扣計算單位。若同一種商品在訂單中被拆成多筆 `OrderItem`（例如兩筆各 6 件的「襪子」），目前實作會分別計算，**各自不足 10 件，皆不觸發折扣**，而非合併為 12 件後計算 1 組折扣。
- **促銷無狀態**：`DoubleElevenDiscount` 不儲存任何狀態，每次 `apply()` 呼叫皆為獨立計算。
- **數值精度**：折扣金額以 Python `float` 計算，未使用 `Decimal`；在單價或數量極大時，存在浮點誤差的潛在風險。

### 尚未涵蓋的情境

- **同種商品拆成多筆 `OrderItem` 的合併計算**：目前不支援，需在 `apply()` 中先以商品名稱分組聚合數量。
- **商品類別（category）限制**：目前折扣適用於所有商品，不受 `category` 限制，spec 中亦未規定類別條件。
- **與其他促銷策略的交互測試**：目前無 scenario 測試 `DoubleElevenDiscount` 與 `ThresholdDiscount` 或 `BuyOneGetOnePromotion` 同時啟用的情形。

---

## 6. 未來開發注意事項

### 新增優惠類型

只需在 `src/promotions.py` 新增一個實作以下簽名的類別：

```python
def apply(self, items: list, original_amount: float, current_discount: float) -> tuple[float, list]:
    ...
```

接著在測試的 Given 步驟中注入至 `OrderService(promotions=[...])` 即可。**不需要修改 `OrderService` 或任何現有類別。**

### 容易受需求變更影響的脆弱點

| 脆弱點 | 說明 |
|--------|------|
| **同種商品多筆合併邏輯** | 若業務規則改為「相同商品名稱的數量應合併計算」，需修改 `DoubleElevenDiscount.apply()` 加入以 `product.name` 分組聚合的邏輯 |
| **折扣比例硬編碼** | 目前 `0.2`（即 20% 折扣）直接寫死在 `apply()` 內；若折扣比例需要設定化，需改為建構子參數 |
| **門檻數量硬編碼** | 目前滿 10 件的門檻直接寫死為 `10`；若門檻需要彈性設定，同樣需改為建構子參數 |
| **step definitions 欄位名稱** | `campaign_steps.py` 的 When step 直接讀取中文欄位名稱（`商品名稱`、`數量`、`單價`），若 feature 檔欄位名稱異動，step 需同步更新 |
