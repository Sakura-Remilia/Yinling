**项目：适老化银龄社区**

**平台：Python Web + REST API**

**数据库：MYSQL**

---

## 角色身份与功能

---

## 一、老人（elderly）

**核心定位：** 服务的享受者，被关怀的中心。

**设计原则：** 极致简洁（大字体、大按钮、语音输入、一键直达）。

### 1. 紧急求助（SOS）
| 功能 | API | 说明 |
|------|-----|------|
| 触发SOS | `POST /sos/trigger` | 发送带定位的紧急求助 |
| 查看我的SOS记录 | `GET /sos/my-alerts` | 查看历史求助记录 |
| 取消SOS | `POST /sos/<id>/cancel` | 取消未响应的求助 |
| 查看SOS详情 | `GET /sos/<id>` | 查看某条SOS详情 |

### 2. 健康监测与提醒
| 功能 | API | 说明 |
|------|-----|------|
| 手动录入健康数据 | `POST /elderly/health-records` | 血压、血糖、心率、体温等 |
| 查看健康记录 | `GET /elderly/health-records` | 分页查看历史记录 |
| 用药提醒设置 | `POST /elderly/medication-reminders` | 设置吃药提醒 |
| 查看用药提醒 | `GET /elderly/medication-reminders` | 查看已设置的提醒 |
| 修改/删除用药提醒 | `PUT/DELETE /elderly/medication-reminders/<id>` | 管理提醒 |
| 复诊提醒设置 | `POST /elderly/appointments` | 设置复诊提醒 |
| 查看/修改/删除复诊提醒 | `GET/PUT/DELETE /elderly/appointments/<id>` | 管理复诊提醒 |

### 3. 一键呼叫服务
| 功能 | API | 说明 |
|------|-----|------|
| 创建服务订单 | `POST /orders` | 选择服务类型、时间下单 |
| 查看我的订单 | `GET /orders` | 查看订单列表 |
| 查看订单详情 | `GET /orders/<id>` | 查看某订单详情 |
| 评价订单 | `POST /orders/<id>/review` | 服务完成后评价 |
| 获取服务分类 | `GET /orders/categories` | 查看可选服务类型 |

### 4. 活动广场与兴趣社交
| 功能 | API | 说明 |
|------|-----|------|
| 查看活动列表 | `GET /public/activities` | 公开的活动列表 |
| 报名活动 | `POST /activities/<id>/register` | 报名参加活动 |
| 查看我的报名 | `GET /activities/my-registrations` | 查看已报名的活动 |
| 取消报名 | `POST /activities/<id>/cancel` | 取消报名 |

### 5. 个人档案管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看档案 | `GET /elderly/profile` | 查看个人基本信息 |
| 更新档案 | `PUT /elderly/profile` | 更新健康状况等 |

### 6. 资讯浏览
| 功能 | API | 说明 |
|------|-----|------|
| 查看新闻 | `GET /public/news` | 获取资讯列表 |
| 查看新闻详情 | `GET /public/news/<id>` | 查看某条资讯 |

---

## 二、志愿者（volunteer）

**核心定位：** 服务的执行者，温情的传递者。

**设计原则：** 任务清晰、反馈便捷、服务留痕。

### 1. 任务接单中心
| 功能 | API | 说明 |
|------|-----|------|
| 查看可接任务 | `GET /volunteer/tasks` | 查看老人发布的需求 |
| 接取任务 | `POST /volunteer/tasks/<id>/accept` | 志愿者抢单 |
| 查看我的订单 | `GET /volunteer/orders` | 查看已接的订单 |

### 2. 服务打卡与记录
| 功能 | API | 说明 |
|------|-----|------|
| 到达签到 | `POST /volunteer/orders/<id>/checkin` | 定位签到开始服务 |
| 完成任务 | `POST /volunteer/orders/<id>/complete` | 结束服务并上传记录 |
| 查看服务记录 | `GET /volunteer/records` | 查看历史服务记录 |

### 3. 积分/时长兑换商城
| 功能 | API | 说明 |
|------|-----|------|
| 查看积分信息 | `GET /volunteer/points` | 查看总积分和服务时长 |
| 查看积分明细 | `GET /volunteer/points/transactions` | 查看积分流水 |
| 查看可兑换商品 | `GET /volunteer/points/products` | 查看积分商城 |
| 兑换商品 | `POST /volunteer/points/exchange/<id>` | 使用积分兑换 |

### 4. 老人护理信息查看
| 功能 | API | 说明 |
|------|-----|------|
| 查看老人护理注意事项 | `GET /volunteer/elderly/<id>/care-info` | 查看服务老人的护理信息 |
| 查看老人健康记录 | `GET /volunteer/elderly/<id>/health-records` | 查看老人健康数据 |

### 5. 个人档案
| 功能 | API | 说明 |
|------|-----|------|
| 查看/更新档案 | `GET/PUT /volunteer/profile` | 查看和更新个人信息 |

---

## 三、工作人员（worker）

**核心定位：** 专业的服务提供者，事务的处理者。

**设计原则：** 高效处理工单，管理服务流程。

### 1. 工单处理系统
| 功能 | API | 说明 |
|------|-----|------|
| 查看可接订单 | `GET /worker/orders` | 查看待接的付费任务 |
| 接取订单 | `POST /worker/orders/<id>/accept` | 工作人员接单 |
| 查看我的订单 | `GET /worker/my-orders` | 查看已接的订单 |
| 确认到达 | `POST /worker/orders/<id>/arrive` | 到达老人位置并签到 |
| 完成任务 | `POST /worker/orders/<id>/complete` | 结束服务 |

### 2. 老人档案管理（动态更新）
| 功能 | API | 说明 |
|------|-----|------|
| 查看老人列表 | `GET /worker/elderly` | 查看本社区老人列表 |
| 查看老人详情 | `GET /worker/elderly/<id>` | 查看老人详细信息 |
| 录入体检数据 | `POST /worker/elderly/<id>/health-records` | 上门体检时录入 |
| 查看健康记录 | `GET /worker/elderly/<id>/health-records` | 查看老人健康历史 |
| 修改健康记录 | `PUT /worker/elderly/<id>/health-records/<rid>` | 修改录入的数据 |
| 删除健康记录 | `DELETE /worker/elderly/<id>/health-records/<rid>` | 删除错误数据 |
| 健康数据统计 | `GET /worker/elderly/<id>/health-stats` | 查看健康趋势和统计 |

### 3. 走访任务执行
| 功能 | API | 说明 |
|------|-----|------|
| 查看走访记录 | `GET /worker/visits` | 查看历史走访 |
| 创建走访任务 | `POST /worker/visits` | 创建新的走访计划 |
| 完成走访 | `POST /worker/visits/<id>/complete` | 提交走访结果（可同步录入健康数据） |

### 4. 服务质量回访
| 功能 | API | 说明 |
|------|-----|------|
| 查看回访记录 | `GET /worker/follow-ups` | 查看历史回访 |
| 创建回访记录 | `POST /worker/follow-ups` | 创建回访记录 |

### 5. 个人档案
| 功能 | API | 说明 |
|------|-----|------|
| 查看/更新档案 | `GET/PUT /worker/profile` | 查看和更新个人信息 |

---

## 四、社区管理员（community_admin）

**核心定位：** 资源调配者，活动组织者，安全监控者。

**设计原则：** 宏观把控，数据驱动决策。

### 1. 大屏监控看板（数据驾驶舱）
| 功能 | API | 说明 |
|------|-----|------|
| 仪表盘统计 | `GET /community-admin/dashboard` | 独居老人数、SOS待处理、订单统计等 |

### 2. 活动发布与管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看活动列表 | `GET /community-admin/activities` | 查看本社区活动 |
| 创建活动 | `POST /community-admin/activities` | 发布新活动 |
| 修改活动 | `PUT /community-admin/activities/<id>` | 编辑活动信息 |

### 3. 人员与权限管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看志愿者列表 | `GET /community-admin/volunteers` | 查看本社区志愿者 |
| 审核志愿者 | `POST /community-admin/volunteers/<id>/verify` | 审核通过志愿者 |
| 查看工作人员列表 | `GET /community-admin/workers` | 查看本社区工作人员 |
| 审核工作人员 | `POST /community-admin/workers/<id>/verify` | 审核通过工作人员 |
| 标记培训完成 | `POST /community-admin/workers/<id>/train` | 标记培训完成 |

### 4. 预警与处置
| 功能 | API | 说明 |
|------|-----|------|
| 查看SOS警报 | `GET /community-admin/sos` | 查看本社区SOS警报 |
| 查看预警通知 | `GET /community-admin/alerts` | 查看系统预警通知 |

### 5. 账号管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看账号列表 | `GET /community-admin/accounts` | 查看本社区所有账号 |
| 社区老人健康统计 | `GET /community-admin/elderly/health-stats` | 社区老人健康概况 |
| 老人健康详情 | `GET /community-admin/elderly/<id>/health-stats` | 单个老人健康详情 |

### 6. 订单管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看订单列表 | `GET /community-admin/orders` | 查看本社区所有订单 |

---

## 五、后台管理员（super_admin）

**核心定位：** 技术保障者，规则制定者，多社区统筹者。

**设计原则：** 系统稳定，数据安全，可扩展性。

### 1. 多层级组织架构管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看社区列表 | `GET /super-admin/communities` | 查看所有社区 |
| 创建社区 | `POST /super-admin/communities` | 新增社区 |
| 修改社区 | `PUT /super-admin/communities/<id>` | 编辑社区信息 |
| 删除社区 | `DELETE /super-admin/communities/<id>` | 删除社区 |

### 2. 用户与角色权限管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看用户列表 | `GET /users` | 查看所有用户 |
| 创建用户 | `POST /users` | 新建用户账号 |
| 查看用户详情 | `GET /users/<id>` | 查看用户信息 |
| 修改用户 | `PUT /users/<id>` | 更新用户信息 |
| 删除用户 | `DELETE /users/<id>` | 删除用户 |
| 重置密码 | `PUT /users/<id>/reset-password` | 重置用户密码 |
| 启用/禁用账号 | `PUT /users/<id>/toggle-active` | 启用或禁用账号 |

### 3. 服务分类管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看服务分类 | `GET /super-admin/service-categories` | 查看所有服务类型 |
| 创建服务分类 | `POST /super-admin/service-categories` | 新增服务类型 |
| 修改服务分类 | `PUT /super-admin/service-categories/<id>` | 编辑服务类型 |
| 删除服务分类 | `DELETE /super-admin/service-categories/<id>` | 删除服务类型 |

### 4. 内容安全审核
| 功能 | API | 说明 |
|------|-----|------|
| 查看新闻列表 | `GET /super-admin/news` | 查看所有新闻 |
| 创建新闻 | `POST /super-admin/news` | 发布新闻 |
| 修改新闻 | `PUT /super-admin/news/<id>` | 编辑新闻 |
| 删除新闻 | `DELETE /super-admin/news/<id>` | 删除新闻 |

### 5. 预警规则管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看预警规则 | `GET /super-admin/alert-rules` | 查看所有预警规则 |
| 创建预警规则 | `POST /super-admin/alert-rules` | 新增预警规则 |
| 修改预警规则 | `PUT /super-admin/alert-rules/<id>` | 编辑预警规则 |
| 删除预警规则 | `DELETE /super-admin/alert-rules/<id>` | 删除预警规则 |

### 6. 积分商品管理
| 功能 | API | 说明 |
|------|-----|------|
| 查看积分商品 | `GET /super-admin/point-products` | 查看所有商品 |
| 创建积分商品 | `POST /super-admin/point-products` | 新增商品 |
| 修改积分商品 | `PUT /super-admin/point-products/<id>` | 编辑商品 |
| 删除积分商品 | `DELETE /super-admin/point-products/<id>` | 删除商品 |

### 7. 系统运维与日志
| 功能 | API | 说明 |
|------|-----|------|
| 系统概览 | `GET /super-admin/dashboard` | 查看系统统计数据 |
| 系统日志 | `GET /super-admin/logs` | 查看操作日志 |

---

## 数据模型关系

```
User
├── role_id → Role (elderly/volunteer/worker/community_admin/super_admin)
├── community_id → Community
├── ElderlyProfile (老人扩展信息)
├── VolunteerProfile (志愿者扩展信息)
├── WorkerProfile (工作人员扩展信息)
└── CommunityAdminProfile (社区管理员扩展信息)

ServiceOrder
├── elderly_id → User (下单老人)
├── provider_id → User (接单人员: worker或volunteer)
├── provider_type: 'worker' | 'volunteer'
├── category_id → ServiceCategory
├── community_id → Community

HealthRecord
├── elderly_id → User (被记录的老人)
├── creator_id → User (录入人员: 老人自己或工作人员)

VisitRecord
├── visitor_id → User (工作人员)
├── elderly_id → User (被走访的老人)

SOSAlert
├── elderly_id → User (求助老人)
├── community_id → Community
├── responder_id → User (响应人员)

Activity
├── organizer_id → User (组织者)
├── community_id → Community
```

---

## 箭头流程

### 1. 服务订单流转图（老人下单 -> 服务完成）

```
老人下单 (POST /orders)
    ↓
系统判断服务类型：
    ├── 付费服务 → 推送给工作人员 (worker)
    └── 志愿/无偿服务 → 推送给志愿者 (volunteer)
    ↓
服务人员接单 (POST /worker/orders/<id>/accept 或 POST /volunteer/tasks/<id>/accept)
    ↓
服务人员到达并签到 (POST /worker/orders/<id>/arrive 或 POST /volunteer/orders/<id>/checkin)
    ↓
服务人员完成任务 (POST /worker/orders/<id>/complete 或 POST /volunteer/orders/<id>/complete)
    ↓
老人评价 (POST /orders/<id>/review)
    ↓
工作人员回访 (POST /worker/follow-ups)
    ↓
流程结束
```

### 2. SOS应急响应流程（老人触发警报 -> 解除）

```
老人触发SOS (POST /sos/trigger)
    ↓
系统生成SOS工单
    ↓
通知紧急联系人（WebSocket推送）
    ↓
响应人员响应 (POST /sos/<id>/respond)
    ↓
响应人员到达现场
    ↓
响应人员解除警报 (POST /sos/<id>/resolve)
    ↓
流程结束
```

### 3. 健康档案录入流程

```
老人申请体检服务
    ↓
工作人员接单
    ↓
工作人员执行体检
    ↓
工作人员录入健康数据 (POST /worker/elderly/<id>/health-records)
    ↓
系统自动检查数据异常 → 异常则创建预警通知
    ↓
健康数据存入 HealthRecord 表
    ↓
老人可查看自己的健康记录 (GET /elderly/health-records)
志愿者可查看服务老人的护理信息 (GET /volunteer/elderly/<id>/care-info)
工作人员可查看本社区老人健康档案 (GET /worker/elderly/<id>/health-records)
社区管理员可查看本社区健康统计 (GET /community-admin/elderly/health-stats)
    ↓
流程结束
```

### 4. 走访任务与健康数据同步

```
工作人员创建走访任务 (POST /worker/visits)
    ↓
工作人员完成走访 (POST /worker/visits/<id>/complete)
    ↓
提交走访结果时可同时录入健康数据 (create_health_record: true, health_data: {...})
    ↓
系统自动创建 HealthRecord
    ↓
如数据异常，自动创建预警通知
    ↓
流程结束
```

---

## 权限控制

| 角色 | 可查看数据 | 可操作 |
|------|-----------|--------|
| 老人 | 自己的档案、订单、健康记录 | 自己的档案、订单、SOS |
| 志愿者 | 服务关联的老人护理信息 | 服务订单、查看老人信息 |
| 工作人员 | 本社区老人档案、健康数据 | 本社区老人健康录入、走访、回访 |
| 社区管理员 | 本社区所有数据 | 本社区人员管理、活动、SOS处理 |
| 超级管理员 | 全部数据 | 全部管理功能 |

---

## 数据库自动更新

项目启动时自动检查并添加缺失的数据库列：

| 表名 | 新增字段 |
|------|---------|
| health_records | heart_rate, temperature, height, weight, vision_left, vision_right, hearing, blood_type, record_date, exam_summary, creator_id |
| service_orders | community_id, check_in_time, check_out_time, price, completion_notes |
| sos_alerts | community_id |

---

*最后更新：2026-04-15*
