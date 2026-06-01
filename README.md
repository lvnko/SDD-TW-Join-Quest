《 臺灣規格驅動開發研究組織 (SDD.TW) 》是一場由《水球軟體學院》發起的技術研究社群，目標是集結全台具備軟體開發能力的工程師，共同推進 AI × SDD/BDD 開發流程的研究與實踐。
「如果大家都關注 AI x SDD/BDD 這件事，台灣軟工進度就有機會超前國外；
當國外 AI 軟工都只會寫 rules 時，我們就已經全部都在寫 spec，產值絕對爆增。」

### 本組織將專注於以下目標
1. 本組織相信 AI x SDD/BDD 的方法，一定能讓 AI 在背景就產出 80%~90% 可靠且正確的程式，而這一定是未來 Vibe Coding 的趨勢，你一定是想要追求最前沿的軟工技術才加入本組織。
2. 組織規劃好了初步研究藍圖，分為底下三大路線
    a. 開發流程全自動化（後端）— Feature file (BDD) 到 API Spec/ERD 到程式
    b. 開發流程全自動化（前端）— 線框 到 User-flow (BDD) 到程式
    c. 回饋流程智能化 (全端) — 前後端整合自動化建立新的驗收測試
這三者只要都研究完成，那 Vibe Coding 才算是成熟，軟體工程師能與與 AI 「平行」合作帶來百倍產出，故稱「AI 百倍軟工研究組織」。

### 歡迎所有人參與
你的參與，不僅代表你願意走在 AI 軟體開發方法論的最前線，更代表你願意投身於一場嚴謹、務實、強調產出價值與技術驗證的研究歷程（所有的研究紀錄都會使用 Github Repository 保存脈絡）。
報名方法：
1. 加入水球軟體學院 Discord：https://discord.gg/uWGTF7RSnW
2. 照著此 Discord 社群內 #加入研究計劃 置頂訊息的指示進行即可成功報名
若你已準備好成為推動 AI × SDD/BDD 開發方法的革新者，誠摯邀請你完成報名，與來自全台的技術夥伴攜手共創。

***

### Python 環境設訂步驟

1. **設定 Global 環境版本：** 專案每個任務都需要運行 `behave` 指令做測試，而此工具需要在 python 3.11.6 上運行，因此需要用以下指令設定環境：
    ```bash
    pyenv global 3.11.6 # 先把 global 的 python 版本設定在 3.11.6
    python3 --version  # 若設定成功，這個指令會回覆 3.11.6
    ```

1. **創建專案虛擬環境：** 
    ```bash
    python3 -m venv .venv # Create a venv using python3.11 (pyenv should have it on your PATH)
    source .venv/bin/activate # Activate it
    pip install behave # Install behave
    behave --no-capture # Now run your test
    ```

2. **恢復虛擬環境：** 當你關掉編輯器 (例：VSCode)，然後第二天又回來開始工作，可以用以下步驟恢復虛擬環境：   
    ```bash
    source .venv/bin/activate
    ```

5. **額外匹步:** To make this automatic so you never have to think about it, add a .envrc file to your repo root:
    ```bash
    echo "source .venv/bin/activate" > .envrc
    ```
    If you have direnv installed, it'll auto-activate the venv every time you cd into the project folder. Worth installing if you switch between projects often.