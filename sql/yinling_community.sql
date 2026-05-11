/*
 Navicat Premium Data Transfer

 Source Server         : admin
 Source Server Type    : MySQL
 Source Server Version : 80100 (8.1.0)
 Source Host           : localhost:3306
 Source Schema         : yinling_community

 Target Server Type    : MySQL
 Target Server Version : 80100 (8.1.0)
 File Encoding         : 65001

 Date: 20/04/2026 17:25:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for activities
-- ----------------------------
DROP TABLE IF EXISTS `activities`;
CREATE TABLE `activities`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `cover_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `activity_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `longitude` float NULL DEFAULT NULL,
  `latitude` float NULL DEFAULT NULL,
  `max_participants` int NULL DEFAULT NULL,
  `current_participants` int NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `organizer_id` int NULL DEFAULT NULL,
  `community_id` int NULL DEFAULT NULL,
  `is_public` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `organizer_id`(`organizer_id` ASC) USING BTREE,
  INDEX `community_id`(`community_id` ASC) USING BTREE,
  CONSTRAINT `activities_ibfk_1` FOREIGN KEY (`organizer_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `activities_ibfk_2` FOREIGN KEY (`community_id`) REFERENCES `communities` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of activities
-- ----------------------------
INSERT INTO `activities` VALUES (1, '太极拳', '每周六、日早上八点，在银龄广场上进行太极拳活动', NULL, 'sports', '2026-03-18 15:09:00', '2039-01-01 15:09:00', '银龄小区门口', NULL, NULL, 50, 0, 'published', 5, NULL, 1, '2026-03-18 07:10:15', '2026-04-16 19:11:58');

-- ----------------------------
-- Table structure for activity_registrations
-- ----------------------------
DROP TABLE IF EXISTS `activity_registrations`;
CREATE TABLE `activity_registrations`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `activity_id` int NOT NULL,
  `elderly_id` int NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `is_waitlist` tinyint(1) NULL DEFAULT NULL,
  `registered_at` datetime NULL DEFAULT NULL,
  `attended` tinyint(1) NULL DEFAULT NULL,
  `attended_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `activity_id`(`activity_id` ASC) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  CONSTRAINT `activity_registrations_ibfk_1` FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `activity_registrations_ibfk_2` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of activity_registrations
-- ----------------------------

-- ----------------------------
-- Table structure for alert_notifications
-- ----------------------------
DROP TABLE IF EXISTS `alert_notifications`;
CREATE TABLE `alert_notifications`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `rule_id` int NULL DEFAULT NULL,
  `user_id` int NULL DEFAULT NULL,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `is_read` tinyint(1) NULL DEFAULT NULL,
  `read_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `rule_id`(`rule_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `alert_notifications_ibfk_1` FOREIGN KEY (`rule_id`) REFERENCES `alert_rules` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `alert_notifications_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of alert_notifications
-- ----------------------------

-- ----------------------------
-- Table structure for alert_rules
-- ----------------------------
DROP TABLE IF EXISTS `alert_rules`;
CREATE TABLE `alert_rules`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `rule_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `threshold` int NULL DEFAULT NULL,
  `time_window_hours` int NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `notify_roles` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of alert_rules
-- ----------------------------

-- ----------------------------
-- Table structure for appointment_reminders
-- ----------------------------
DROP TABLE IF EXISTS `appointment_reminders`;
CREATE TABLE `appointment_reminders`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `elderly_id` int NOT NULL,
  `hospital` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `doctor` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `appointment_time` datetime NOT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `is_completed` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  CONSTRAINT `appointment_reminders_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of appointment_reminders
-- ----------------------------

-- ----------------------------
-- Table structure for communities
-- ----------------------------
DROP TABLE IF EXISTS `communities`;
CREATE TABLE `communities`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `parent_id` int NULL DEFAULT NULL,
  `level` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `parent_id`(`parent_id` ASC) USING BTREE,
  CONSTRAINT `communities_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `communities` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of communities
-- ----------------------------
INSERT INTO `communities` VALUES (1, '东湖学院', '文化大道301号', '666', '这是一个示例社区', NULL, 1, '2026-03-17 09:17:33');

-- ----------------------------
-- Table structure for community_admin_profiles
-- ----------------------------
DROP TABLE IF EXISTS `community_admin_profiles`;
CREATE TABLE `community_admin_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NULL DEFAULT NULL,
  `position` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `managed_community_id` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `managed_community_id`(`managed_community_id` ASC) USING BTREE,
  CONSTRAINT `community_admin_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `community_admin_profiles_ibfk_2` FOREIGN KEY (`managed_community_id`) REFERENCES `communities` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of community_admin_profiles
-- ----------------------------
INSERT INTO `community_admin_profiles` VALUES (1, 5, '社区皇帝', '皇帝', NULL, '2026-03-18 08:03:47');
INSERT INTO `community_admin_profiles` VALUES (2, 9, NULL, NULL, NULL, '2026-04-04 16:07:06');

-- ----------------------------
-- Table structure for community_announcements
-- ----------------------------
DROP TABLE IF EXISTS `community_announcements`;
CREATE TABLE `community_announcements`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `cover_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `community_id` int NULL DEFAULT NULL,
  `publisher_id` int NULL DEFAULT NULL,
  `is_pinned` tinyint(1) NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `published_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `community_id`(`community_id` ASC) USING BTREE,
  INDEX `publisher_id`(`publisher_id` ASC) USING BTREE,
  CONSTRAINT `community_announcements_ibfk_1` FOREIGN KEY (`community_id`) REFERENCES `communities` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `community_announcements_ibfk_2` FOREIGN KEY (`publisher_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 42 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of community_announcements
-- ----------------------------
INSERT INTO `community_announcements` VALUES (1, '关于清明节假期服务安排的通知', '各位社区居民：\n\n清明节假期即将来临，现将假期期间服务安排通知如下：\n\n1. 社区服务中心4月4日-6日放假调休，4月7日（周日）正常上班。\n\n2. 紧急求助服务24小时正常运行，如有需要请拨打热线电话：400-123-4567。\n\n3. 社区餐厅假期期间正常供餐，营业时间为早7:00-晚19:00。\n\n4. 4月5日上午9:00将在社区广场举行清明祭扫活动，欢迎各位居民参加。\n\n祝各位居民清明节安康！\n\n银龄社区服务中心\n2024年4月1日', '', 1, 1, 1, 1, '2024-04-01 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (2, '社区免费体检通知', '各位老年居民：\n\n为关爱老年人身体健康，我社区联合社区卫生服务中心开展免费体检活动。\n\n【体检时间】4月15日-4月20日，每天上午8:00-11:30\n【体检地点】社区服务中心一楼健康体检室\n【体检项目】常规体格检查、血压血糖检测、心电图、肝肾功能、腹部B超\n【注意事项】请携带身份证和社保卡，体检前一天清淡饮食\n\n名额有限，请提前预约！\n\n银龄社区服务中心\n2024年4月8日', '', 1, 1, 1, 1, '2024-04-08 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (3, '社区花园改造施工公告', '各位居民：为给社区居民提供更好的休闲环境，我社区将对中心花园进行升级改造。\n\n【施工时间】4月10日-4月25日\n【施工内容】更新健身器材、增设休闲座椅、绿化景观提升、安装夜间照明\n【注意事项】施工期间花园区域暂停开放，请居民绕行注意安全\n\n因施工给您带来的不便，敬请谅解！\n\n银龄社区服务中心\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (4, '防范电信诈骗安全提示', '各位社区居民：近期电信诈骗案件频发，请提高警惕。\n\n【常见诈骗手法】冒充公检法转账、冒充熟人借钱、短信中奖汇款、网络购物退款骗银行卡\n\n【防骗要点】不轻信陌生来电、不向陌生人转账、不随意泄露个人信息、遇可疑及时报警\n\n如有疑问请拨打：110或联系社区工作人员\n\n银龄社区警务室\n2024年4月3日', '', 1, 1, 0, 1, '2024-04-03 11:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (5, '老年大学春季班报名通知', '各位老年朋友：银龄老年大学2024年春季班现在开始报名！\n\n【开设课程】书法基础班、国画入门班、太极拳班、智能手机应用班、广场舞班\n【报名条件】社区60岁以上老年人，身体健康\n【报名时间】4月1日-4月10日\n【报名地点】社区服务中心二楼老年大学办公室\n\n电话：400-123-4567 联系人：王老师\n\n银龄老年大学\n2024年3月28日', '', 1, 1, 0, 1, '2024-03-28 16:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (6, '社区餐饮服务时间调整通知', '各位居民：社区餐厅服务时间调整如下：\n\n【新营业时间】早餐：7:00-9:00 午餐：11:30-13:30 晚餐：17:30-19:30\n\n【优惠活动】60岁以上老人8折优惠，80岁以上7折，行动不便可送餐\n【送餐服务】提前1小时拨打400-123-4567\n\n银龄社区餐厅\n2024年4月1日', '', 1, 1, 0, 1, '2024-04-01 08:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (7, '电梯维护保养通知', '各位居民：为确保电梯安全运行，物业将对电梯进行例行维护保养。\n\n【维护时间】4月8日 9:00-17:00\n【涉及楼栋】1号楼、2号楼电梯\n【注意事项】维护期间电梯暂停使用，老年人如需帮助可联系物业\n\n因维护给您带来的不便，敬请谅解！\n\n银龄社区物业\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (8, '社区志愿者招募通知', '各位居民：为弘扬志愿服务精神，现面向社区招募志愿者。\n\n【招募对象】18-70岁身体健康居民\n【服务内容】关爱独居老人、社区环境美化、活动协助、文明引导\n【志愿者福利】获得服务时长证明、积分兑换礼品、年度优秀志愿者评选\n【报名方式】现场/电话/微信报名\n\n让我们一起传递爱心，共建美好家园！\n\n银龄社区志愿者服务站\n2024年4月2日', '', 1, 1, 0, 1, '2024-04-02 15:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (9, '五一劳动节放假安排', '各位居民：五一劳动节放假安排如下：\n\n【放假时间】5月1日-5月5日放假调休，5月6日（周一）正常上班\n【服务安排】社区服务中心5月1日-3日休息，紧急求助服务24小时运行\n\n假期期间值班电话：400-123-4567\n\n祝各位居民五一劳动节快乐！\n\n银龄社区服务中心\n2024年4月20日', '', 1, 1, 0, 1, '2024-04-20 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (10, '夏季用电安全温馨提示', '各位居民：夏季用电高峰期来临，请注意以下事项：\n\n【安全用电】不私拉乱接、不使用大功率电器、定期检查家用电器\n【空调使用】温度不低于26℃，避免长时间连续使用，定期清洗过滤网\n【应急处理】电器冒烟起火立即断电，用干粉灭火器，切勿用水\n\n服务热线：400-123-4567\n\n银龄社区物业\n2024年4月25日', '', 1, 1, 0, 1, '2024-04-25 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (11, '关于清明节假期服务安排的通知', '各位社区居民：\n\n清明节假期即将来临，现将假期期间服务安排通知如下：\n\n1. 社区服务中心4月4日-6日放假调休，4月7日（周日）正常上班。\n\n2. 紧急求助服务24小时正常运行，如有需要请拨打热线电话：400-123-4567。\n\n3. 社区餐厅假期期间正常供餐，营业时间为早7:00-晚19:00。\n\n4. 4月5日上午9:00将在社区广场举行清明祭扫活动，欢迎各位居民参加。\n\n祝各位居民清明节安康！\n\n银龄社区服务中心\n2024年4月1日', '', 1, 1, 1, 1, '2024-04-01 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (12, '社区免费体检通知', '各位老年居民：\n\n为关爱老年人身体健康，我社区联合社区卫生服务中心开展免费体检活动。\n\n【体检时间】4月15日-4月20日，每天上午8:00-11:30\n【体检地点】社区服务中心一楼健康体检室\n【体检项目】常规体格检查、血压血糖检测、心电图、肝肾功能、腹部B超\n【注意事项】请携带身份证和社保卡，体检前一天清淡饮食\n\n名额有限，请提前预约！\n\n银龄社区服务中心\n2024年4月8日', '', 1, 1, 1, 1, '2024-04-08 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (13, '社区花园改造施工公告', '各位居民：为给社区居民提供更好的休闲环境，我社区将对中心花园进行升级改造。\n\n【施工时间】4月10日-4月25日\n【施工内容】更新健身器材、增设休闲座椅、绿化景观提升、安装夜间照明\n【注意事项】施工期间花园区域暂停开放，请居民绕行注意安全\n\n因施工给您带来的不便，敬请谅解！\n\n银龄社区服务中心\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (14, '防范电信诈骗安全提示', '各位社区居民：近期电信诈骗案件频发，请提高警惕。\n\n【常见诈骗手法】冒充公检法转账、冒充熟人借钱、短信中奖汇款、网络购物退款骗银行卡\n\n【防骗要点】不轻信陌生来电、不向陌生人转账、不随意泄露个人信息、遇可疑及时报警\n\n如有疑问请拨打：110或联系社区工作人员\n\n银龄社区警务室\n2024年4月3日', '', 1, 1, 0, 1, '2024-04-03 11:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (15, '老年大学春季班报名通知', '各位老年朋友：银龄老年大学2024年春季班现在开始报名！\n\n【开设课程】书法基础班、国画入门班、太极拳班、智能手机应用班、广场舞班\n【报名条件】社区60岁以上老年人，身体健康\n【报名时间】4月1日-4月10日\n【报名地点】社区服务中心二楼老年大学办公室\n\n电话：400-123-4567 联系人：王老师\n\n银龄老年大学\n2024年3月28日', '', 1, 1, 0, 1, '2024-03-28 16:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (16, '社区餐饮服务时间调整通知', '各位居民：社区餐厅服务时间调整如下：\n\n【新营业时间】早餐：7:00-9:00 午餐：11:30-13:30 晚餐：17:30-19:30\n\n【优惠活动】60岁以上老人8折优惠，80岁以上7折，行动不便可送餐\n【送餐服务】提前1小时拨打400-123-4567\n\n银龄社区餐厅\n2024年4月1日', '', 1, 1, 0, 1, '2024-04-01 08:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (17, '电梯维护保养通知', '各位居民：为确保电梯安全运行，物业将对电梯进行例行维护保养。\n\n【维护时间】4月8日 9:00-17:00\n【涉及楼栋】1号楼、2号楼电梯\n【注意事项】维护期间电梯暂停使用，老年人如需帮助可联系物业\n\n因维护给您带来的不便，敬请谅解！\n\n银龄社区物业\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (18, '社区志愿者招募通知', '各位居民：为弘扬志愿服务精神，现面向社区招募志愿者。\n\n【招募对象】18-70岁身体健康居民\n【服务内容】关爱独居老人、社区环境美化、活动协助、文明引导\n【志愿者福利】获得服务时长证明、积分兑换礼品、年度优秀志愿者评选\n【报名方式】现场/电话/微信报名\n\n让我们一起传递爱心，共建美好家园！\n\n银龄社区志愿者服务站\n2024年4月2日', '', 1, 1, 0, 1, '2024-04-02 15:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (19, '五一劳动节放假安排', '各位居民：五一劳动节放假安排如下：\n\n【放假时间】5月1日-5月5日放假调休，5月6日（周一）正常上班\n【服务安排】社区服务中心5月1日-3日休息，紧急求助服务24小时运行\n\n假期期间值班电话：400-123-4567\n\n祝各位居民五一劳动节快乐！\n\n银龄社区服务中心\n2024年4月20日', '', 1, 1, 0, 1, '2024-04-20 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (20, '夏季用电安全温馨提示', '各位居民：夏季用电高峰期来临，请注意以下事项：\n\n【安全用电】不私拉乱接、不使用大功率电器、定期检查家用电器\n【空调使用】温度不低于26℃，避免长时间连续使用，定期清洗过滤网\n【应急处理】电器冒烟起火立即断电，用干粉灭火器，切勿用水\n\n服务热线：400-123-4567\n\n银龄社区物业\n2024年4月25日', '', 1, 1, 0, 1, '2024-04-25 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (21, '关于清明节假期服务安排的通知', '各位社区居民：\n\n清明节假期即将来临，现将假期期间服务安排通知如下：\n\n1. 社区服务中心4月4日-6日放假调休，4月7日（周日）正常上班。\n\n2. 紧急求助服务24小时正常运行，如有需要请拨打热线电话：400-123-4567。\n\n3. 社区餐厅假期期间正常供餐，营业时间为早7:00-晚19:00。\n\n4. 4月5日上午9:00将在社区广场举行清明祭扫活动，欢迎各位居民参加。\n\n祝各位居民清明节安康！\n\n银龄社区服务中心\n2024年4月1日', '', 1, 1, 1, 1, '2024-04-01 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (22, '社区免费体检通知', '各位老年居民：\n\n为关爱老年人身体健康，我社区联合社区卫生服务中心开展免费体检活动。\n\n【体检时间】4月15日-4月20日，每天上午8:00-11:30\n【体检地点】社区服务中心一楼健康体检室\n【体检项目】常规体格检查、血压血糖检测、心电图、肝肾功能、腹部B超\n【注意事项】请携带身份证和社保卡，体检前一天清淡饮食\n\n名额有限，请提前预约！\n\n银龄社区服务中心\n2024年4月8日', '', 1, 1, 1, 1, '2024-04-08 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (23, '社区花园改造施工公告', '各位居民：为给社区居民提供更好的休闲环境，我社区将对中心花园进行升级改造。\n\n【施工时间】4月10日-4月25日\n【施工内容】更新健身器材、增设休闲座椅、绿化景观提升、安装夜间照明\n【注意事项】施工期间花园区域暂停开放，请居民绕行注意安全\n\n因施工给您带来的不便，敬请谅解！\n\n银龄社区服务中心\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (24, '防范电信诈骗安全提示', '各位社区居民：近期电信诈骗案件频发，请提高警惕。\n\n【常见诈骗手法】冒充公检法转账、冒充熟人借钱、短信中奖汇款、网络购物退款骗银行卡\n\n【防骗要点】不轻信陌生来电、不向陌生人转账、不随意泄露个人信息、遇可疑及时报警\n\n如有疑问请拨打：110或联系社区工作人员\n\n银龄社区警务室\n2024年4月3日', '', 1, 1, 0, 1, '2024-04-03 11:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (25, '老年大学春季班报名通知', '各位老年朋友：银龄老年大学2024年春季班现在开始报名！\n\n【开设课程】书法基础班、国画入门班、太极拳班、智能手机应用班、广场舞班\n【报名条件】社区60岁以上老年人，身体健康\n【报名时间】4月1日-4月10日\n【报名地点】社区服务中心二楼老年大学办公室\n\n电话：400-123-4567 联系人：王老师\n\n银龄老年大学\n2024年3月28日', '', 1, 1, 0, 1, '2024-03-28 16:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (26, '社区餐饮服务时间调整通知', '各位居民：社区餐厅服务时间调整如下：\n\n【新营业时间】早餐：7:00-9:00 午餐：11:30-13:30 晚餐：17:30-19:30\n\n【优惠活动】60岁以上老人8折优惠，80岁以上7折，行动不便可送餐\n【送餐服务】提前1小时拨打400-123-4567\n\n银龄社区餐厅\n2024年4月1日', '', 1, 1, 0, 1, '2024-04-01 08:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (27, '电梯维护保养通知', '各位居民：为确保电梯安全运行，物业将对电梯进行例行维护保养。\n\n【维护时间】4月8日 9:00-17:00\n【涉及楼栋】1号楼、2号楼电梯\n【注意事项】维护期间电梯暂停使用，老年人如需帮助可联系物业\n\n因维护给您带来的不便，敬请谅解！\n\n银龄社区物业\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (28, '社区志愿者招募通知', '各位居民：为弘扬志愿服务精神，现面向社区招募志愿者。\n\n【招募对象】18-70岁身体健康居民\n【服务内容】关爱独居老人、社区环境美化、活动协助、文明引导\n【志愿者福利】获得服务时长证明、积分兑换礼品、年度优秀志愿者评选\n【报名方式】现场/电话/微信报名\n\n让我们一起传递爱心，共建美好家园！\n\n银龄社区志愿者服务站\n2024年4月2日', '', 1, 1, 0, 1, '2024-04-02 15:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (29, '五一劳动节放假安排', '各位居民：五一劳动节放假安排如下：\n\n【放假时间】5月1日-5月5日放假调休，5月6日（周一）正常上班\n【服务安排】社区服务中心5月1日-3日休息，紧急求助服务24小时运行\n\n假期期间值班电话：400-123-4567\n\n祝各位居民五一劳动节快乐！\n\n银龄社区服务中心\n2024年4月20日', '', 1, 1, 0, 1, '2024-04-20 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (30, '夏季用电安全温馨提示', '各位居民：夏季用电高峰期来临，请注意以下事项：\n\n【安全用电】不私拉乱接、不使用大功率电器、定期检查家用电器\n【空调使用】温度不低于26℃，避免长时间连续使用，定期清洗过滤网\n【应急处理】电器冒烟起火立即断电，用干粉灭火器，切勿用水\n\n服务热线：400-123-4567\n\n银龄社区物业\n2024年4月25日', '', 1, 1, 0, 1, '2024-04-25 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (31, '关于清明节假期服务安排的通知', '各位社区居民：\n\n清明节假期即将来临，现将假期期间服务安排通知如下：\n\n1. 社区服务中心4月4日-6日放假调休，4月7日（周日）正常上班。\n\n2. 紧急求助服务24小时正常运行，如有需要请拨打热线电话：400-123-4567。\n\n3. 社区餐厅假期期间正常供餐，营业时间为早7:00-晚19:00。\n\n4. 4月5日上午9:00将在社区广场举行清明祭扫活动，欢迎各位居民参加。\n\n祝各位居民清明节安康！\n\n银龄社区服务中心\n2024年4月1日', '', 1, 1, 1, 1, '2024-04-01 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (32, '社区免费体检通知', '各位老年居民：\n\n为关爱老年人身体健康，我社区联合社区卫生服务中心开展免费体检活动。\n\n【体检时间】4月15日-4月20日，每天上午8:00-11:30\n【体检地点】社区服务中心一楼健康体检室\n【体检项目】常规体格检查、血压血糖检测、心电图、肝肾功能、腹部B超\n【注意事项】请携带身份证和社保卡，体检前一天清淡饮食\n\n名额有限，请提前预约！\n\n银龄社区服务中心\n2024年4月8日', '', 1, 1, 1, 1, '2024-04-08 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (33, '社区花园改造施工公告', '各位居民：为给社区居民提供更好的休闲环境，我社区将对中心花园进行升级改造。\n\n【施工时间】4月10日-4月25日\n【施工内容】更新健身器材、增设休闲座椅、绿化景观提升、安装夜间照明\n【注意事项】施工期间花园区域暂停开放，请居民绕行注意安全\n\n因施工给您带来的不便，敬请谅解！\n\n银龄社区服务中心\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (34, '防范电信诈骗安全提示', '各位社区居民：近期电信诈骗案件频发，请提高警惕。\n\n【常见诈骗手法】冒充公检法转账、冒充熟人借钱、短信中奖汇款、网络购物退款骗银行卡\n\n【防骗要点】不轻信陌生来电、不向陌生人转账、不随意泄露个人信息、遇可疑及时报警\n\n如有疑问请拨打：110或联系社区工作人员\n\n银龄社区警务室\n2024年4月3日', '', 1, 1, 0, 1, '2024-04-03 11:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (35, '老年大学春季班报名通知', '各位老年朋友：银龄老年大学2024年春季班现在开始报名！\n\n【开设课程】书法基础班、国画入门班、太极拳班、智能手机应用班、广场舞班\n【报名条件】社区60岁以上老年人，身体健康\n【报名时间】4月1日-4月10日\n【报名地点】社区服务中心二楼老年大学办公室\n\n电话：400-123-4567 联系人：王老师\n\n银龄老年大学\n2024年3月28日', '', 1, 1, 0, 1, '2024-03-28 16:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (36, '社区餐饮服务时间调整通知', '各位居民：社区餐厅服务时间调整如下：\n\n【新营业时间】早餐：7:00-9:00 午餐：11:30-13:30 晚餐：17:30-19:30\n\n【优惠活动】60岁以上老人8折优惠，80岁以上7折，行动不便可送餐\n【送餐服务】提前1小时拨打400-123-4567\n\n银龄社区餐厅\n2024年4月1日', '', 1, 1, 0, 1, '2024-04-01 08:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (37, '电梯维护保养通知', '各位居民：为确保电梯安全运行，物业将对电梯进行例行维护保养。\n\n【维护时间】4月8日 9:00-17:00\n【涉及楼栋】1号楼、2号楼电梯\n【注意事项】维护期间电梯暂停使用，老年人如需帮助可联系物业\n\n因维护给您带来的不便，敬请谅解！\n\n银龄社区物业\n2024年4月5日', '', 1, 1, 0, 1, '2024-04-05 09:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (38, '社区志愿者招募通知', '各位居民：为弘扬志愿服务精神，现面向社区招募志愿者。\n\n【招募对象】18-70岁身体健康居民\n【服务内容】关爱独居老人、社区环境美化、活动协助、文明引导\n【志愿者福利】获得服务时长证明、积分兑换礼品、年度优秀志愿者评选\n【报名方式】现场/电话/微信报名\n\n让我们一起传递爱心，共建美好家园！\n\n银龄社区志愿者服务站\n2024年4月2日', '', 1, 1, 0, 1, '2024-04-02 15:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (39, '五一劳动节放假安排', '各位居民：五一劳动节放假安排如下：\n\n【放假时间】5月1日-5月5日放假调休，5月6日（周一）正常上班\n【服务安排】社区服务中心5月1日-3日休息，紧急求助服务24小时运行\n\n假期期间值班电话：400-123-4567\n\n祝各位居民五一劳动节快乐！\n\n银龄社区服务中心\n2024年4月20日', '', 1, 1, 0, 1, '2024-04-20 10:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (40, '夏季用电安全温馨提示', '各位居民：夏季用电高峰期来临，请注意以下事项：\n\n【安全用电】不私拉乱接、不使用大功率电器、定期检查家用电器\n【空调使用】温度不低于26℃，避免长时间连续使用，定期清洗过滤网\n【应急处理】电器冒烟起火立即断电，用干粉灭火器，切勿用水\n\n服务热线：400-123-4567\n\n银龄社区物业\n2024年4月25日', '', 1, 1, 0, 1, '2024-04-25 14:00:00', NULL, NULL);
INSERT INTO `community_announcements` VALUES (41, '银龄社区超市开业大酬宾', '银龄社区超市开业大酬宾，商品打折，快来抢购了', '', NULL, 1, 0, 1, '2026-04-16 19:33:25', '2026-04-16 19:33:25', '2026-04-16 19:33:25');

-- ----------------------------
-- Table structure for elderly_profiles
-- ----------------------------
DROP TABLE IF EXISTS `elderly_profiles`;
CREATE TABLE `elderly_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NULL DEFAULT NULL,
  `birth_date` date NULL DEFAULT NULL,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `longitude` float NULL DEFAULT NULL,
  `latitude` float NULL DEFAULT NULL,
  `emergency_contact` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `emergency_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `emergency_contact2` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `emergency_phone2` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `health_status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `chronic_diseases` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `allergies` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `is_living_alone` tinyint(1) NULL DEFAULT NULL,
  `children_info` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `medical_history` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `display_mode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'standard',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `elderly_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of elderly_profiles
-- ----------------------------
INSERT INTO `elderly_profiles` VALUES (1, 2, '2026-03-18', 'male', '123123', '中国', NULL, NULL, '儿子', '110', '', '', '', '', '空气过敏', 1, '', '', '2026-03-17 09:39:30', '2026-03-18 00:39:31', 'standard');
INSERT INTO `elderly_profiles` VALUES (2, 6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, '2026-04-04 15:25:49', '2026-04-04 15:25:49', 'standard');

-- ----------------------------
-- Table structure for follow_up_records
-- ----------------------------
DROP TABLE IF EXISTS `follow_up_records`;
CREATE TABLE `follow_up_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NULL DEFAULT NULL,
  `follower_id` int NOT NULL,
  `elderly_id` int NOT NULL,
  `follow_up_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `follow_up_time` datetime NULL DEFAULT NULL,
  `satisfaction_level` int NULL DEFAULT NULL,
  `feedback` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `issues_found` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `resolution` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `order_id`(`order_id` ASC) USING BTREE,
  INDEX `follower_id`(`follower_id` ASC) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  CONSTRAINT `follow_up_records_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `service_orders` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `follow_up_records_ibfk_2` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `follow_up_records_ibfk_3` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of follow_up_records
-- ----------------------------

-- ----------------------------
-- Table structure for health_records
-- ----------------------------
DROP TABLE IF EXISTS `health_records`;
CREATE TABLE `health_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `elderly_id` int NOT NULL,
  `record_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` float NULL DEFAULT NULL,
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `systolic` int NULL DEFAULT NULL,
  `diastolic` int NULL DEFAULT NULL,
  `blood_sugar` float NULL DEFAULT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `recorded_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `heart_rate` int NULL DEFAULT NULL,
  `temperature` float NULL DEFAULT NULL,
  `height` float NULL DEFAULT NULL,
  `weight` float NULL DEFAULT NULL,
  `vision_left` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `vision_right` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `hearing` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `blood_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `record_date` date NULL DEFAULT NULL,
  `exam_summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `creator_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  CONSTRAINT `health_records_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of health_records
-- ----------------------------
INSERT INTO `health_records` VALUES (1, 2, 'blood_pressure', NULL, NULL, 60, 40, NULL, '', '2026-03-17 13:48:36', '2026-03-17 13:48:36', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `health_records` VALUES (2, 2, 'blood_sugar', NULL, NULL, NULL, NULL, 1, '', '2026-03-17 13:48:42', '2026-03-17 13:48:42', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `health_records` VALUES (3, 6, 'blood_pressure', NULL, NULL, 120, 90, NULL, '', '2026-04-16 18:00:43', '2026-04-16 18:00:43', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `health_records` VALUES (4, 6, 'blood_sugar', NULL, NULL, NULL, NULL, 30, '', '2026-04-16 18:01:07', '2026-04-16 18:01:07', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- ----------------------------
-- Table structure for medication_reminders
-- ----------------------------
DROP TABLE IF EXISTS `medication_reminders`;
CREATE TABLE `medication_reminders`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `elderly_id` int NOT NULL,
  `medication_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `dosage` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `frequency` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `reminder_times` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `start_date` date NULL DEFAULT NULL,
  `end_date` date NULL DEFAULT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  CONSTRAINT `medication_reminders_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of medication_reminders
-- ----------------------------

-- ----------------------------
-- Table structure for news
-- ----------------------------
DROP TABLE IF EXISTS `news`;
CREATE TABLE `news`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `cover_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `news_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `author_id` int NULL DEFAULT NULL,
  `is_published` tinyint(1) NULL DEFAULT NULL,
  `published_at` datetime NULL DEFAULT NULL,
  `view_count` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `community_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `author_id`(`author_id` ASC) USING BTREE,
  CONSTRAINT `news_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of news
-- ----------------------------
INSERT INTO `news` VALUES (1, '震惊！！！伤害老年人的食物里竟然有它！！！', '铁皮、充电器、电池、沙发、地板砖！\r\n这些都是对中老年人危害性极大的食物。', NULL, 'health', 1, 0, NULL, 0, '2026-03-18 08:49:42', '2026-03-18 08:49:42', NULL);
INSERT INTO `news` VALUES (2, '春季养生：老年人应如何科学进补', '春季是养生好时节，科学进补注意以下几点：\n\n【饮食原则】宜甘温忌辛辣，多吃新鲜蔬果，适量蛋白质\n【推荐食谱】红枣山药粥健脾养胃、枸杞菊花茶清肝明目、香菇鸡汤增强免疫力\n【运动建议】春季适合户外散步、太极拳，时间宜在上午9-11点\n【注意事项】进补要适量，根据体质选择，慢性病遵医嘱\n\n银龄健康资讯\n2024年4月1日', '', 'health', 1, 1, '2024-04-01 09:00:00', 0, NULL, NULL, NULL);
INSERT INTO `news` VALUES (3, '高血压患者如何科学运动', '高血压是老年人常见慢性病，科学运动有助控制血压。\n\n【运动益处】降血压、改善心血管、减重、缓解焦虑\n【适合运动】散步每天30-60分钟、太极拳每周3-5次、慢跑、游泳\n【运动禁忌】避免剧烈运动、不做低头超过心脏水平的动作、血压过高时暂停\n【注意事项】运动前测血压、循序渐进、随身带急救药、运动后不立即洗澡\n\n银龄健康资讯\n2024年4月3日', '', 'health', 1, 1, '2024-04-03 10:00:00', 0, NULL, NULL, NULL);
INSERT INTO `news` VALUES (4, '老年糖尿病患者的饮食指南', '糖尿病是老年人常见疾病，饮食控制是治疗基础。\n\n【饮食原则】控制总热量、少量多餐、粗细搭配、清淡少盐\n【推荐食物】粗粮、燕麦荞麦、蔬菜、苦瓜黄瓜西红柿、苹果猕猴桃、鱼虾豆腐\n【饮食禁忌】甜食糖果、高脂肪食物、稀饭粥类升糖快、水果罐头\n【健康食谱】早餐牛奶全麦面包鸡蛋，午餐杂粮饭清蒸鱼凉拌菜，晚餐荞麦面豆腐蔬菜汤\n\n银龄健康资讯\n2024年4月5日', '', 'health', 1, 1, '2024-04-05 11:00:00', 0, NULL, NULL, NULL);
INSERT INTO `news` VALUES (5, '如何预防老年人跌倒', '跌倒是老年人意外伤害主因之一，预防非常重要。\n\n【跌倒风险】骨质疏松、视力下降、平衡能力减退、药物副作用\n【预防措施】家庭环境改造保持地面干燥安装扶手、适当运动每天散步练习太极、定期检查视力和骨密度\n【应急处理】如不慎跌倒不要急于扶起，先检查伤情\n\n银龄健康资讯\n2024年4月7日', '', 'health', 1, 1, '2024-04-07 14:00:00', 0, NULL, NULL, NULL);
INSERT INTO `news` VALUES (6, '老年认知症早期识别与护理', '老年认知症是影响生活质量的重要疾病，早期识别很关键。\n\n【早期症状】记忆力下降尤其是短期记忆、语言表达困难、定向力障碍、判断力下降、性格改变\n【预防措施】多动脑多运动多社交、健康饮食、良好睡眠\n【家属护理】保持耐心理解、建立规律生活、安全管理、寻求专业支持\n【就医指征】发现症状应尽早就医，早期干预可延缓进展\n\n银龄健康资讯\n2024年4月10日', '', 'health', 1, 1, '2024-04-10 09:00:00', 1, NULL, '2026-04-16 19:13:58', NULL);
INSERT INTO `news` VALUES (7, '老年人心理健康维护指南', '心理健康是健康重要部分，老年人应重视心理健康维护。\n\n【常见心理问题】退休综合征、孤独抑郁、焦虑失眠、丧偶之痛\n【心理调适】培养兴趣爱好书法绘画音乐、保持社交、适度运动、学会放松深呼吸冥想\n【寻求帮助】遇心理困扰及时寻求家人支持或专业心理咨询\n【社区资源】银龄社区心理咨询热线：400-123-4567 周一至周五9:00-17:00\n\n银龄健康资讯\n2024年4月12日', '', 'health', 1, 1, '2024-04-12 15:00:00', 0, NULL, NULL, NULL);
INSERT INTO `news` VALUES (8, '骨质疏松的预防与治疗', '骨质疏松是老年人常见骨骼疾病，了解预防和治疗方法很重要。\n\n【高危人群】老年女性绝经后、长期服用激素、钙摄入不足、缺乏运动\n【预防措施】合理补钙每天1000-1200mg、补充维生素D每天800-1000IU、适度运动多晒太阳15-30分钟\n【饮食建议】奶制品、豆制品、海产品、绿叶蔬菜\n【治疗方法】钙剂、维生素D、双膦酸盐等，遵医嘱用药\n\n银龄健康资讯\n2024年4月15日', '', 'health', 1, 1, '2024-04-15 10:00:00', 1, NULL, '2026-04-20 02:35:59', NULL);
INSERT INTO `news` VALUES (9, '老年人睡眠障碍的改善方法', '睡眠问题是老年人常见困扰，良好睡眠对健康至关重要。\n\n【常见问题】入睡困难、睡眠浅易醒、早醒、白天嗜睡\n【改善方法】规律作息固定时间睡觉起床午睡不超1小时、营造良好睡眠环境卧室安静黑暗温度18-22℃、睡前避免咖啡因剧烈运动手机\n【助眠食物】热牛奶、蜂蜜水、酸枣仁粥\n【就医指征】长期失眠影响生活质量时应及时就医\n\n银龄健康资讯\n2024年4月18日', '', 'health', 1, 1, '2024-04-18 16:00:00', 0, NULL, NULL, NULL);
INSERT INTO `news` VALUES (10, '心脑血管疾病的预防', '心脑血管疾病是老年人健康主要威胁，预防重于治疗。\n\n【危险因素】高血压、高血脂、糖尿病、吸烟、肥胖、缺乏运动\n【预防措施】健康饮食低盐低脂多蔬果、适度运动每周至少150分钟、控制三高定期监测、戒烟限酒、心态平和\n【早期信号】胸闷心悸头晕肢体麻木等应引起重视\n\n银龄健康资讯\n2024年4月20日', '', 'health', 1, 1, '2024-04-20 11:00:00', 0, NULL, NULL, NULL);
INSERT INTO `news` VALUES (11, '老年人用药安全须知', '老年人常患多种慢性病，用药安全非常重要。\n\n【用药原则】遵医嘱服药、不擅自停药换药、了解药物副作用、定期复查\n【常见问题】记忆力差漏服药物、同时服用多种药物、自行购买非处方药、听信偏方\n【安全建议】使用药盒帮助按时服药、保留用药清单、定期清理家庭药箱、就医时告知所有用药\n【注意事项】不服用过期药物、正确储存、关注药物相互作用\n\n银龄健康资讯\n2024年4月22日', '', 'health', 1, 1, '2024-04-22 14:00:00', 6, NULL, '2026-04-16 19:13:49', NULL);

-- ----------------------------
-- Table structure for point_exchanges
-- ----------------------------
DROP TABLE IF EXISTS `point_exchanges`;
CREATE TABLE `point_exchanges`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NULL DEFAULT NULL,
  `points_used` int NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `exchange_time` datetime NULL DEFAULT NULL,
  `processed_at` datetime NULL DEFAULT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `product_id`(`product_id` ASC) USING BTREE,
  CONSTRAINT `point_exchanges_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `point_exchanges_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `point_products` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of point_exchanges
-- ----------------------------

-- ----------------------------
-- Table structure for point_products
-- ----------------------------
DROP TABLE IF EXISTS `point_products`;
CREATE TABLE `point_products`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `points_required` int NOT NULL,
  `stock` int NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of point_products
-- ----------------------------
INSERT INTO `point_products` VALUES (1, '一个鸡蛋', '一个，鸡蛋。', NULL, 10, 20, 1, '2026-03-18 08:50:57');
INSERT INTO `point_products` VALUES (2, '两个鸡蛋', '嘎达。嘎达。', NULL, 60, 2, 1, '2026-03-18 08:59:09');

-- ----------------------------
-- Table structure for point_transactions
-- ----------------------------
DROP TABLE IF EXISTS `point_transactions`;
CREATE TABLE `point_transactions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `amount` int NOT NULL,
  `transaction_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `related_record_id` int NULL DEFAULT NULL,
  `related_record_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `balance_after` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `point_transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of point_transactions
-- ----------------------------

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `permissions` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles` VALUES (1, 'elderly', '老人', NULL);
INSERT INTO `roles` VALUES (2, 'volunteer', '志愿者', NULL);
INSERT INTO `roles` VALUES (3, 'worker', '工作人员', NULL);
INSERT INTO `roles` VALUES (4, 'community_admin', '社区管理员', NULL);
INSERT INTO `roles` VALUES (5, 'super_admin', '后台管理员', NULL);

-- ----------------------------
-- Table structure for service_categories
-- ----------------------------
DROP TABLE IF EXISTS `service_categories`;
CREATE TABLE `service_categories`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `price_range` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `is_free` tinyint(1) NULL DEFAULT NULL,
  `icon` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sort_order` int NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of service_categories
-- ----------------------------
INSERT INTO `service_categories` VALUES (1, '助浴服务', '专业助浴服务，安全舒适', NULL, 0, NULL, 1, 1, '2026-03-17 09:17:33');
INSERT INTO `service_categories` VALUES (2, '家政清洁', '家庭清洁打扫服务', NULL, 0, NULL, 2, 1, '2026-03-17 09:17:33');
INSERT INTO `service_categories` VALUES (3, '理发服务', '上门理发服务', NULL, 0, NULL, 3, 1, '2026-03-17 09:17:33');
INSERT INTO `service_categories` VALUES (4, '陪诊服务', '医院陪诊服务', NULL, 0, NULL, 4, 1, '2026-03-17 09:17:33');
INSERT INTO `service_categories` VALUES (5, '送餐服务', '营养餐配送服务', NULL, 0, NULL, 5, 1, '2026-03-17 09:17:33');
INSERT INTO `service_categories` VALUES (6, '孤独陪伴', '志愿者陪伴聊天服务', NULL, 1, NULL, 6, 1, '2026-03-17 09:17:33');
INSERT INTO `service_categories` VALUES (7, '代购代办', '志愿者代购代办服务', NULL, 1, NULL, 7, 1, '2026-03-17 09:17:33');

-- ----------------------------
-- Table structure for service_orders
-- ----------------------------
DROP TABLE IF EXISTS `service_orders`;
CREATE TABLE `service_orders`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `elderly_id` int NOT NULL,
  `category_id` int NOT NULL,
  `service_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_free` tinyint(1) NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `longitude` float NULL DEFAULT NULL,
  `latitude` float NULL DEFAULT NULL,
  `contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `scheduled_time` datetime NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `provider_id` int NULL DEFAULT NULL,
  `provider_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `accepted_at` datetime NULL DEFAULT NULL,
  `arrived_at` datetime NULL DEFAULT NULL,
  `started_at` datetime NULL DEFAULT NULL,
  `completed_at` datetime NULL DEFAULT NULL,
  `service_photos` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `service_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `rating` int NULL DEFAULT NULL,
  `review` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `reviewed_at` datetime NULL DEFAULT NULL,
  `cancel_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `cancelled_at` datetime NULL DEFAULT NULL,
  `cancelled_by` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `community_id` int NULL DEFAULT NULL,
  `check_in_time` datetime NULL DEFAULT NULL,
  `check_out_time` datetime NULL DEFAULT NULL,
  `price` float NULL DEFAULT NULL,
  `completion_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `order_no`(`order_no` ASC) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  INDEX `category_id`(`category_id` ASC) USING BTREE,
  INDEX `provider_id`(`provider_id` ASC) USING BTREE,
  INDEX `cancelled_by`(`cancelled_by` ASC) USING BTREE,
  CONSTRAINT `service_orders_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `service_orders_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `service_categories` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `service_orders_ibfk_3` FOREIGN KEY (`provider_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `service_orders_ibfk_4` FOREIGN KEY (`cancelled_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of service_orders
-- ----------------------------
INSERT INTO `service_orders` VALUES (1, 'SO20260317220007V3590R', 2, 1, '助浴服务', 0, 'None', NULL, NULL, '13812345678', NULL, '', 'completed', 8, 'worker', '2026-04-16 18:43:06', '2026-04-16 18:43:12', '2026-04-16 18:43:12', '2026-04-16 18:43:23', NULL, '已完成', NULL, NULL, NULL, NULL, NULL, NULL, '2026-03-17 14:00:08', '2026-04-16 18:43:23', NULL, NULL, NULL, NULL, NULL);
INSERT INTO `service_orders` VALUES (2, 'SO202604061330320GQM16', 6, 2, '家政清洁', 0, 'None', NULL, NULL, '13800001111', '2026-04-06 13:30:00', '房屋请假', 'completed', 8, 'worker', '2026-04-06 05:31:36', '2026-04-16 18:43:32', '2026-04-16 18:43:32', '2026-04-16 18:43:40', NULL, '已完成', NULL, NULL, NULL, NULL, NULL, NULL, '2026-04-06 05:30:33', '2026-04-16 18:43:40', NULL, NULL, NULL, NULL, NULL);
INSERT INTO `service_orders` VALUES (3, 'SO202604170242349UAP3F', 6, 1, '助浴服务', 0, '银龄社区', NULL, NULL, '13800001111', '2026-04-04 15:00:00', '帮忙洗澡', 'completed', 8, 'worker', '2026-04-16 19:09:13', '2026-04-16 19:09:27', '2026-04-16 19:09:27', '2026-04-16 19:09:34', NULL, '已完成', NULL, NULL, NULL, NULL, NULL, NULL, '2026-04-16 18:42:34', '2026-04-16 19:09:34', NULL, NULL, NULL, NULL, NULL);

-- ----------------------------
-- Table structure for sos_alerts
-- ----------------------------
DROP TABLE IF EXISTS `sos_alerts`;
CREATE TABLE `sos_alerts`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `alert_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `elderly_id` int NOT NULL,
  `longitude` float NULL DEFAULT NULL,
  `latitude` float NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `triggered_at` datetime NULL DEFAULT NULL,
  `responder_id` int NULL DEFAULT NULL,
  `responded_at` datetime NULL DEFAULT NULL,
  `arrived_at` datetime NULL DEFAULT NULL,
  `resolved_at` datetime NULL DEFAULT NULL,
  `resolution_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `resolution_photos` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `is_escalated` tinyint(1) NULL DEFAULT NULL,
  `escalated_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `community_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `alert_no`(`alert_no` ASC) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  INDEX `responder_id`(`responder_id` ASC) USING BTREE,
  CONSTRAINT `sos_alerts_ibfk_1` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `sos_alerts_ibfk_2` FOREIGN KEY (`responder_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sos_alerts
-- ----------------------------

-- ----------------------------
-- Table structure for system_logs
-- ----------------------------
DROP TABLE IF EXISTS `system_logs`;
CREATE TABLE `system_logs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NULL DEFAULT NULL,
  `action` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `module` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `ip_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `user_agent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `request_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `request_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `request_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `response_status` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `system_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of system_logs
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `real_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `role_id` int NULL DEFAULT NULL,
  `community_id` int NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  `last_login` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `phone`(`phone` ASC) USING BTREE,
  UNIQUE INDEX `ix_users_username`(`username` ASC) USING BTREE,
  INDEX `role_id`(`role_id` ASC) USING BTREE,
  INDEX `community_id`(`community_id` ASC) USING BTREE,
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`community_id`) REFERENCES `communities` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'scrypt:32768:8:1$eDdqmvS7eOif42vL$cdcfbaf770b9eab4425fb79c09a8c4139f72837913b539d9b9448f25821344af3476c4c6881146b3b4a16d79113594514e4626b42285ff248582efa714f75d68', '系统管理员', '13800000000', 'admin@yinling.com', 'default_avatar.svg', 5, NULL, 1, '2026-03-17 09:17:33', '2026-04-20 09:01:48', '2026-04-20 09:01:48');
INSERT INTO `users` VALUES (2, '1', 'scrypt:32768:8:1$Nn5NOrIEQzqW2Jmy$2054b9b1464e1cad2cc85b91db35cb43129f4ccf1d3dfa64c1df0c0b8dbf8364deb7eaaa90650dce145204e1f81f446c9133bda839031c2a10abee6553b9d2e1', '1号老头', '13812345678', '1@qq.com', 'default_avatar.svg', 1, NULL, 1, '2026-03-17 09:39:30', '2026-04-16 07:08:31', '2026-04-16 07:08:31');
INSERT INTO `users` VALUES (3, '2', 'scrypt:32768:8:1$5gVLpccuY6otLEMp$f44441acb3340236bf1934c2e4f6cc640031bd16392c19391f9a765fffd6fa09ddfd084909d66751ce2f95b390794ecd43ba4b34a6531293e88dacda11b74986', '雷锋', '13912345678', '2@qq.com', 'default_avatar.svg', 2, NULL, 1, '2026-03-18 05:56:54', '2026-03-18 06:11:54', '2026-03-18 06:11:54');
INSERT INTO `users` VALUES (4, '3', 'scrypt:32768:8:1$5Rzwq65l2gGXnVRY$59dd9c4876243a12df8690d02c780ffa28d836243eec3e09c2f8100f8029d9e453c782c02a2a4a2e2b5b5d8e666cddeeed24d12bea2a12e3a34a3a5d6f252827', '工作人员1', '13012345678', '3@qq.com', 'default_avatar.svg', 3, NULL, 1, '2026-03-18 06:13:38', '2026-03-18 08:02:36', '2026-03-18 06:13:41');
INSERT INTO `users` VALUES (5, '4', 'scrypt:32768:8:1$lo9f5HvNQPhd5JUt$b725de42b5d14f2e04d2e5cf9a32f210f490f97f888b593dff062ee5f18eafd3ad4da6f4d6adb6aa428c50527739d298466087d621f236c76e16c0629d2009dd', '社区管理员', '13112345678', '4@qq.com', 'default_avatar.svg', 4, NULL, 1, '2026-03-18 06:45:58', '2026-03-18 08:03:10', '2026-03-18 08:03:10');
INSERT INTO `users` VALUES (6, 'test1', 'scrypt:32768:8:1$iye0ANsYVNmV4U1T$90e8013d309696d955f801f3e1802ac2de169d0e50d57d44077601d6f3b81c20c26564487ea11304c92eccecd5cbb34d2d580dd458c6da159d19b42cf1ede72b', 'test1', '13800001111', '13800001111@qq.com', 'default_avatar.svg', 1, NULL, 1, '2026-04-04 15:25:49', '2026-04-20 09:00:05', '2026-04-20 09:00:05');
INSERT INTO `users` VALUES (7, 'test11', 'scrypt:32768:8:1$Hb2ZDbkvMu8Pf7I2$c18256509643542cdd89b891a33302ae0dd1a0560b33a0d4a92126db6c7c347f1dfaadf9a8bb5b07dca9c88193c1cbdd09f7b03f7c4d68dcca3668b3e41e930a', 'test11', '13900001111', '13900001111@qq.com', 'default_avatar.svg', 2, NULL, 1, '2026-04-04 15:38:29', '2026-04-20 09:00:24', '2026-04-20 09:00:24');
INSERT INTO `users` VALUES (8, 'test111', 'scrypt:32768:8:1$mVP3P4Q1nK2iGZhW$e8d21efc16e01a975e2eba0baee3e8b1812c10a32bc5bea3597087d973c00e29e99c3dec6b4ac86963dbe2814f0338b17969ef24d4fe7859f41563b003e121cf', 'test111', '14000001111', '14000001111@qq.com', 'default_avatar.svg', 3, NULL, 1, '2026-04-04 15:40:22', '2026-04-20 09:00:37', '2026-04-20 09:00:37');
INSERT INTO `users` VALUES (9, 'test1111', 'scrypt:32768:8:1$5ann40tzwmMVOrGc$ae7c87f8de36c9b6c718e16b05eac09b00e6fc860fd069e0278dfeaa1b0d78c397ff9bb4b5e238ca1c91a17d91cda17cf416a3efe55467396c5c0a402c369242', 'test1111', '14100001111', '14100001111@qq.com', 'default_avatar.svg', 4, NULL, 1, '2026-04-04 15:41:55', '2026-04-20 09:00:58', '2026-04-20 09:00:58');

-- ----------------------------
-- Table structure for visit_records
-- ----------------------------
DROP TABLE IF EXISTS `visit_records`;
CREATE TABLE `visit_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `visitor_id` int NOT NULL,
  `elderly_id` int NOT NULL,
  `visit_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `scheduled_time` datetime NULL DEFAULT NULL,
  `actual_time` datetime NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `longitude` float NULL DEFAULT NULL,
  `latitude` float NULL DEFAULT NULL,
  `health_status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `needs` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `photos` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `visitor_id`(`visitor_id` ASC) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  CONSTRAINT `visit_records_ibfk_1` FOREIGN KEY (`visitor_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `visit_records_ibfk_2` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of visit_records
-- ----------------------------
INSERT INTO `visit_records` VALUES (1, 4, 2, '健康检查', '2026-03-18 14:45:00', NULL, 'pending', NULL, NULL, NULL, NULL, '看老头死没死', NULL, '2026-03-18 06:45:23');
INSERT INTO `visit_records` VALUES (2, 8, 6, '常规走访', '2026-04-04 15:00:00', '2026-04-16 18:44:55', 'completed', NULL, NULL, '良好', '无', '无', NULL, '2026-04-16 18:44:39');

-- ----------------------------
-- Table structure for volunteer_profiles
-- ----------------------------
DROP TABLE IF EXISTS `volunteer_profiles`;
CREATE TABLE `volunteer_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NULL DEFAULT NULL,
  `birth_date` date NULL DEFAULT NULL,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `longitude` float NULL DEFAULT NULL,
  `latitude` float NULL DEFAULT NULL,
  `skills` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `service_areas` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `total_service_hours` float NULL DEFAULT NULL,
  `total_points` int NULL DEFAULT NULL,
  `is_verified` tinyint(1) NULL DEFAULT NULL,
  `verified_at` datetime NULL DEFAULT NULL,
  `bio` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `volunteer_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of volunteer_profiles
-- ----------------------------
INSERT INTO `volunteer_profiles` VALUES (1, 3, NULL, '', '666', '北京', NULL, NULL, '看电视', '中国', 0, 0, 1, '2026-03-18 07:08:48', '我会看电视', '2026-03-18 05:56:54', '2026-03-18 07:08:48');
INSERT INTO `volunteer_profiles` VALUES (2, 7, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 1, '2026-04-04 15:42:11', NULL, '2026-04-04 15:38:29', '2026-04-04 15:42:11');

-- ----------------------------
-- Table structure for volunteer_service_records
-- ----------------------------
DROP TABLE IF EXISTS `volunteer_service_records`;
CREATE TABLE `volunteer_service_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `volunteer_id` int NOT NULL,
  `order_id` int NULL DEFAULT NULL,
  `elderly_id` int NULL DEFAULT NULL,
  `service_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `start_time` datetime NULL DEFAULT NULL,
  `end_time` datetime NULL DEFAULT NULL,
  `duration_minutes` int NULL DEFAULT NULL,
  `check_in_longitude` float NULL DEFAULT NULL,
  `check_in_latitude` float NULL DEFAULT NULL,
  `check_out_longitude` float NULL DEFAULT NULL,
  `check_out_latitude` float NULL DEFAULT NULL,
  `service_photos` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `service_notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `points_earned` int NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `volunteer_id`(`volunteer_id` ASC) USING BTREE,
  INDEX `order_id`(`order_id` ASC) USING BTREE,
  INDEX `elderly_id`(`elderly_id` ASC) USING BTREE,
  CONSTRAINT `volunteer_service_records_ibfk_1` FOREIGN KEY (`volunteer_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `volunteer_service_records_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `service_orders` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `volunteer_service_records_ibfk_3` FOREIGN KEY (`elderly_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of volunteer_service_records
-- ----------------------------

-- ----------------------------
-- Table structure for worker_profiles
-- ----------------------------
DROP TABLE IF EXISTS `worker_profiles`;
CREATE TABLE `worker_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NULL DEFAULT NULL,
  `birth_date` date NULL DEFAULT NULL,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `longitude` float NULL DEFAULT NULL,
  `latitude` float NULL DEFAULT NULL,
  `skills` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `service_areas` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `work_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `is_trained` tinyint(1) NULL DEFAULT NULL,
  `trained_at` datetime NULL DEFAULT NULL,
  `training_certificate` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `is_verified` tinyint(1) NULL DEFAULT NULL,
  `verified_at` datetime NULL DEFAULT NULL,
  `bio` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `total_orders` int NULL DEFAULT NULL,
  `rating` float NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `worker_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of worker_profiles
-- ----------------------------
INSERT INTO `worker_profiles` VALUES (1, 4, NULL, '', '222', '拆哪', NULL, NULL, '玩手机', '拆哪', '全职', 1, '2026-03-18 07:08:50', NULL, 1, '2026-03-18 07:08:53', '666', 0, 5, '2026-03-18 06:13:38', '2026-03-18 07:08:53');
INSERT INTO `worker_profiles` VALUES (2, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, '2026-04-04 15:42:17', NULL, 1, '2026-04-04 15:42:19', NULL, 3, 5, '2026-04-04 15:40:22', '2026-04-16 19:09:34');

SET FOREIGN_KEY_CHECKS = 1;
