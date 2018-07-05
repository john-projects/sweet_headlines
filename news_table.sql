CREATE DATABASE IF NOT EXISTS `news`;

USE `news`;

DROP TABLE IF EXISTS `news_info`;

CREATE TABLE `news_info` (
	`id` int(21) NOT NULL AUTO_INCREMENT,
	`timestamp` timestamp DEFAULT CURRENT_TIMESTAMP NULL COMMENT '爬取时间',
	`title` varchar(255) NOT NULL COMMENT '新闻的标题',
	`news_web_source` varchar(20) NOT NULL COMMENT '新闻爬取来源网站',
	`news_web_source_url` varchar(255) NOT NULL COMMENT '新闻爬取来源网站网址',
	`ep_source` varchar(255) NOT NULL COMMENT '新闻初始来源网站',
	`editor` varchar(50) NOT NULL COMMENT '新闻编辑',
	`news_text` text NOT NULL COMMENT '新闻详情',

	PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;