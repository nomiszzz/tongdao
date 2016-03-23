/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50624
 Source Host           : localhost
 Source Database       : tongdao

 Target Server Type    : MySQL
 Target Server Version : 50624
 File Encoding         : utf-8

 Date: 03/23/2016 18:00:40 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `admin`
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL COMMENT '管理员用户名',
  `password` varchar(40) NOT NULL COMMENT '管理员密码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Records of `admin`
-- ----------------------------
BEGIN;
INSERT INTO `admin` VALUES ('1', 'master', '21232f297a57a5a743894a0e4a801fc3');
COMMIT;

-- ----------------------------
--  Table structure for `award`
-- ----------------------------
DROP TABLE IF EXISTS `award`;
CREATE TABLE `award` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) DEFAULT NULL COMMENT '活动奖品',
  `provide` varchar(150) DEFAULT NULL COMMENT '提供商',
  `image` varchar(100) DEFAULT NULL COMMENT '奖品图片',
  `score` int(8) DEFAULT NULL COMMENT '奖品点数',
  `status` tinyint(1) DEFAULT '1' COMMENT '是否有效',
  `counts` int(8) DEFAULT '0' COMMENT '数量',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Records of `award`
-- ----------------------------

-- ----------------------------
--  Table structure for `banner`
-- ----------------------------
DROP TABLE IF EXISTS `banner`;
CREATE TABLE `banner` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `name` varchar(20) DEFAULT NULL,
  `image` varchar(40) DEFAULT NULL,
  `status` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Records of `banner`
-- ----------------------------

-- ----------------------------
--  Table structure for `pet`
-- ----------------------------
DROP TABLE IF EXISTS `pet`;
CREATE TABLE `pet` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `uid` int(8) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL COMMENT '星座类型',
  `score` int(8) DEFAULT NULL COMMENT '点数',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Records of `pet`
-- ----------------------------
BEGIN;
INSERT INTO `pet` VALUES ('4', '1', 'mojie', '-295', '2016-03-17 22:30:41');
COMMIT;

-- ----------------------------
--  Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(8) NOT NULL AUTO_INCREMENT COMMENT '用户id',
  `nickname` varchar(120) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '微信昵称',
  `avatar` varchar(150) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '微信头像',
  `openid` varchar(60) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '微信 openid',
  `sex` tinyint(1) DEFAULT '0' COMMENT '性别',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
--  Records of `user`
-- ----------------------------
BEGIN;
INSERT INTO `user` VALUES ('1', '\\u4e2d\\u56fd\\u4eba\\U0001f604', 'http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/46', 'OPENID', '1');
COMMIT;

-- ----------------------------
--  Table structure for `winning`
-- ----------------------------
DROP TABLE IF EXISTS `winning`;
CREATE TABLE `winning` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `uid` int(8) DEFAULT NULL,
  `aid` int(11) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL COMMENT '兑换码',
  `status` tinyint(1) DEFAULT '0' COMMENT '是否兑换了',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
--  Records of `winning`
-- ----------------------------


SET FOREIGN_KEY_CHECKS = 1;
