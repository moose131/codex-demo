# codex-demo 速查清单（Mac/Win 通用）

## 1) 开始工作前（同步）
git pull

## 2) 运行单元测试
pytest -q

## 3) 人类验收（示例）
rm -f expenses.demo.json out.csv
EXPENSE_TRACKER_FILE=./expenses.demo.json python -m expense_tracker add 12.5 coffee "latte"
EXPENSE_TRACKER_FILE=./expenses.demo.json python -m expense_tracker add 30 groceries
EXPENSE_TRACKER_FILE=./expenses.demo.json python -m expense_tracker export out.csv
cat out.csv

## 4) 提交与推送
git add -A
git commit -m "your message"
git push

## 5) 用中文驱动 Codex（示例）
codex
在 Codex 里输入：请阅读 AGENTS.md，完成 TASKLIST.md 中的第 N 项；添加测试；运行测试并修复；最后中文汇报。
