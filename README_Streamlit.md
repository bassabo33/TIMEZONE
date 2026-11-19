# 全球時間比較器（Streamlit）

## 本機執行

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

執行後，瀏覽器會開啟 Streamlit 網頁。

## 部署到 Streamlit Community Cloud

1. 在 GitHub 建立一個新的 repository。
2. 將 `app.py` 與 `requirements.txt` 上傳到 repository 根目錄。
3. 登入 [Streamlit Community Cloud](https://share.streamlit.io/)。
4. 選擇 **Create app**，指定剛才的 repository、branch，以及主程式路徑 `app.py`。
5. 按下 **Deploy**，等待部署完成即可取得網頁網址。

此程式使用 `zoneinfo` 與 `tzdata` 處理各城市時區及夏令時間。
