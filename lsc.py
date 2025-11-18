from playwright.sync_api import sync_playwright
import time
import random
import schedule
import jpholiday
from datetime import datetime
import re
import slackweb
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")
ESTATES_PATH = Path(__file__).with_name("estates.json")

def load_slack_webhook_url():
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "config.json が見つかりません。config.example.json を複製し slack_webhook_url を設定してください。"
        ) from exc

    url = config.get("slack_webhook_url")
    if not url:
        raise RuntimeError("config.json に slack_webhook_url が設定されていません。")
    return url

SLACK_WEBHOOK_URL = load_slack_webhook_url()

# 推奨 ＞ % sudo pmset -a disablesleep 1

def load_prev_estates():
    try:
        with ESTATES_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("estates.json が見つからないため空の状態から開始します。")
        return {}

def common_process_run(playwright, func):
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "--- 開始 ---")

    # --- start ---
    browser = playwright.chromium.launch(headless=True, slow_mo=1000)
    # browser = playwright.chromium.launch(headless=False, slow_mo=1000, devtools=True)
    page = browser.new_page()
    page.on("load", lambda: sleep_random(7))

    func(playwright, page)

    # ---------------------
    # page.close()
    browser.close()
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "--- 完了 ---")

def main_logic(playwright, page):
    notice = []

    prev_estates = load_prev_estates()

    estates = get_all_estate(page)

    for title in estates:
        if title not in prev_estates:
            notice.append("+ {}".format(title))

    for title in prev_estates:
        if title not in estates:
            notice.append("- {}".format(title))

    with ESTATES_PATH.open("w", encoding="utf-8") as f:
        json.dump(estates, f, ensure_ascii=False, indent=2)

    if len(notice) > 0:
        slack = slackweb.Slack(url=SLACK_WEBHOOK_URL)
        notice_text = "\n".join(notice)
        slack.notify(text="<!channel>\n{}".format(notice_text))

def get_all_estate (page):
    estates = {}
    page.goto("https://www.loadstarcapital.com/ja/business/corporatefunding.html")
    page.locator("p.more").click()
    name_all = page.locator("div.text-section div.rich-text p span").all()
    for span in name_all:
        text = span.inner_text().rstrip()
        if text:
            estates[span.inner_text().rstrip()] = 1
    return estates

def sleep_random (max_seconds=2):
    seconds = random.random() * max_seconds
    print("sleep {:.1f}s".format(seconds))
    time.sleep(seconds)

def run():
    print("run start")
    with sync_playwright() as playwright:
        # common_process_run(playwright, main_logic)
        schedule.every(8).hours.do(common_process_run, playwright, main_logic)
        while True:
            schedule.run_pending()
            time.sleep(1)

try:
	run()
finally:
        slack = slackweb.Slack(url=SLACK_WEBHOOK_URL)
        slack.notify(text="<!channel>\nscript end")
