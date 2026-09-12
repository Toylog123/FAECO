# 统一命令入口。用法：make help
SHELL := bash

.PHONY: help check record manifest test

help:           ## 显示可用命令
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-12s %s\n", $$1, $$2}'

check:          ## 项目健康检查（交接就绪度）
	bash code/scripts/check_project.sh

record:         ## 记录检查（今日是否已更新）
	bash code/scripts/check_record.sh

manifest:       ## 生成基线 SHA-256 清单
	bash code/scripts/make_manifest.sh

test:           ## 运行测试（技术栈相关，请按需定义）
	@echo "请按技术栈在 Makefile 中定义 test 目标"
