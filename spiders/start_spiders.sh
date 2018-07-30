#!/usr/bin/sh
nohup /john/dreams/sweet_headlines/spiders/tx_spider/tx_spider.py & > /john/dreams/sweet_headlines/spiders/spider.log &
nohup /john/dreams/sweet_headlines/spiders/wy_spider/wy_spider.py & > /john/dreams/sweet_headlines/spiders/spider.log &