# 功能交接文件：訂單定價與促銷邏輯

## 1. Feature 概述

本功能實作電商平台的**訂單結帳促銷計算邏輯**。顧客將商品加入訂單後，系統依據目前啟用的促銷方案（滿額折扣、買一送一）自動計算原始金額、折扣金額與應付總金額，並同時更新顧客實際收到的商品數量。

- 對應 spec 檔案：`docs/specs/order.feature`

---

## 2. 實作架構摘要

### 核心類別

| 類別 | 檔案 | 職責 |
|---|---|---|
| `Product` | `src/entities.py` | 商品資料值物件，持有名稱、單價、分類 |
| `OrderItem` | `src/entities.py` | 訂單明細值物件，關聯一個 `Product` 並記錄數量 |
| `Order` | `src/entities.py` | 結帳結果值物件，持有明細清單、原始金額、折扣、應付總金額 |
| `ThresholdDiscount` | `src/promotions.py` | 促銷策略：滿額折扣，原始金額達門檻時扣減固定金額 |
| `BuyOneGetOnePromotion` | `src/promotions.py` | 促銷策略：美妝買一送一，每條美妝訂單明細增加 1 件贈品 |
| `OrderService` | `src/order_service.py` | 結帳服務，接收 `OrderItem` 清單，套用所有促銷策略，回傳 `Order` |

### 依賴關係

```
OrderService
  ├── 依賴 entities.py（Order、OrderItem）
  └── 持有 promotions 清單（ThresholdDiscount、BuyOneGetOnePromotion）
        └── 促銷類別依賴 entities.py（OrderItem，用於 BOGO 建立贈品明細）
```

### 各檔案路徑與用途

```
src/
  entities.py          # 資料模型：Product、OrderItem、Order
  promotions.py        # 促銷策略實作：ThresholdDiscount、BuyOneGetOnePromotion
  order_service.py     # 結帳主邏輯：OrderService.checkout()

features/
  order.feature        # BDD 驗收情境（6 個 scenario）
  environment.py       # Behave 測試環境設定（sys.path 注入、context 初始化）
  steps/
    order_steps.py     # 所有 Given / When / Then 步驟定義

docs/
  specs/order.feature  # 原始需求 spec
  design/ERD.png       # 實體關係設計圖
  design/OOD.png       # 物件導向設計圖
```

---

## 3. 商業邏輯重點

### 結帳流程（`OrderService.checkout()`）

1. 計算 `original_amount`：所有輸入明細的 `unit_price × quantity` 加總。
2. 依序對每個促銷策略呼叫 `promotion.apply(items, original_amount, current_discount)`，取回更新後的 discount 與 items。
3. `total_amount = original_amount - discount`。
4. 回傳 `Order(result_items, original_amount, discount, total_amount)`。

### 促銷策略規則

**ThresholdDiscount（滿額折扣）**
- 若 `original_amount >= threshold`，則 `discount += discount_amount`。
- **邊界條件**：門檻判斷使用 `>=`，恰好等於門檻時折扣成立。
- 折扣計算基準為 **原始金額**（`original_amount`），不受其他促銷影響，不會因為先套用其他促銷而改變是否達標。

**BuyOneGetOnePromotion（美妝買一送一）**
- 對 `items` 清單中每一條 `category == 'cosmetics'` 的明細，建立新的 `OrderItem`，其 `quantity = 原本數量 + 1`。
- 非美妝分類的明細直接保留，不做任何修改。
- **重要邊界條件：贈品以「訂單明細（order line）」為單位，而非以「購買單位數」為單位。** 無論同一明細購買幾件，一律僅贈送 1 件。
  - 例：口紅 ×1 → 口紅 ×2（+1 件）
  - 例：口紅 ×2 → 口紅 ×3（+1 件，不是 +2 件）
- BOGO 僅修改商品數量，**不影響金額計算**（原始金額以購買數量為準，贈品不計費）。

### 促銷疊加

- 多個促銷依 `promotions` 清單順序依序套用。
- `ThresholdDiscount` 與 `BuyOneGetOnePromotion` 可同時啟用，互不干擾：前者只修改折扣數字，後者只修改商品明細清單。

---

## 4. 測試覆蓋摘要

| Scenario 名稱 | 核心測試行為 |
|---|---|
| Single product without promotions | 無促銷時，totalAmount = 單價 × 數量 |
| Threshold discount applies when subtotal reaches 1000 | 原始金額達門檻（1600 ≥ 1000），折扣 100，totalAmount = 1500 |
| Buy-one-get-one for cosmetics - multiple products | 兩條美妝明細各自獲得 +1 贈品，金額不變 |
| Buy-one-get-one for cosmetics - same product twice | 同一美妝明細購買 2 件，僅贈送 1 件（共 3 件），金額不變 |
| Buy-one-get-one for cosmetics - mixed categories | 非美妝明細不受 BOGO 影響，僅美妝明細獲贈 |
| Multiple promotions stacked | 滿額折扣與 BOGO 同時作用，折扣以原始金額計算，商品數量正確疊加 |

**最終測試執行結果：**
- 1 feature passed, 0 failed, 0 skipped
- **6 scenarios passed, 0 failed, 0 skipped**
- **25 steps passed, 0 failed, 0 skipped**

---

## 5. 已知限制與假設

### 設計假設

1. **促銷策略以 duck typing 實作**：所有促銷類別只需實作 `apply(items, original_amount, current_discount) -> (discount, items)` 介面，未使用抽象基底類別（ABC）。新增促銷類別只需遵循此簽名即可，無強制繼承。
2. **BOGO 的贈品邏輯以「明細行數」為單位**：此行為源自 spec 中 Scenario 4（口紅 ×2 → 口紅 ×3）的明確定義，並非通用的「每買一件送一件」規則。
3. **金額型別為 `float`**：目前使用 Python float，在大量計算時可能有浮點數精度問題。生產環境建議改用 `decimal.Decimal`。
4. **分類比對為字串完全比對**：`category == 'cosmetics'` 區分大小寫，分類值由呼叫端傳入，未做正規化處理。
5. **`OrderItem` 在 BOGO 中為不可變處理**：BOGO 不修改原始 `OrderItem`，而是建立新的 `OrderItem` 物件，確保輸入資料不被污染。
6. **OrderService 不持有狀態**：每次 `checkout()` 呼叫是無狀態的，促銷清單在初始化時決定，不在結帳過程中動態變更。

### 目前未涵蓋的情境

- 折扣金額超過原始金額時（`total_amount` 可能為負數），未做下限保護。
- 同一促銷套用多次（例如兩個不同門檻的 `ThresholdDiscount` 同時啟用）的行為未明確測試。
- 空訂單（`items = []`）的結帳行為未測試（目前會回傳 `total_amount = 0`，但未驗證）。
- 促銷策略的執行順序若調換（先 BOGO 後 threshold vs. 先 threshold 後 BOGO）對結果的影響未測試；就目前邏輯而言，因 threshold 使用 `original_amount`，順序不影響結果。

---

## 6. 未來開發注意事項

### 新增促銷類型

1. 在 `src/promotions.py` 新增促銷類別，實作 `apply(items, original_amount, current_discount)` 方法，回傳 `(new_discount, new_items)` tuple。
2. 在 `features/steps/order_steps.py` 新增對應的 `@given` 步驟，建立促銷物件並附加到 `context.promotions`，再重建 `context.order_service`。
3. 在 `features/order.feature` 或新的 feature file 中補充 scenario。
4. **不需要修改 `OrderService`**——其促銷迭代邏輯對所有符合介面的促銷類別通用。

### 容易受影響的脆弱點

| 脆弱點 | 影響範圍 | 說明 |
|---|---|---|
| BOGO 的「+1 per line」規則 | `BuyOneGetOnePromotion.apply()` | 若業務需求改為「每買 N 件送 1 件」，需重寫此方法；現有 4 個 BOGO scenario 都需重新驗證 |
| Threshold 使用 `original_amount` | `ThresholdDiscount.apply()`、`OrderService.checkout()` | 若門檻改為以「折後金額」計算，需同步修改 `checkout()` 的促銷呼叫順序與傳入參數 |
| 分類字串 `'cosmetics'` 硬編碼 | `BuyOneGetOnePromotion.apply()` | 若分類體系調整（如改用 enum 或 ID），需更新比對邏輯及所有測試資料 |
| 促銷套用順序 | `OrderService.__init__()` 的 `promotions` 清單 | 目前由呼叫端控制順序；若新增的促銷策略之間有相依性（如 A 必須在 B 之前），需在 `OrderService` 加入排序或優先權機制 |
