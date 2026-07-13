#时间管理 #时间管理 #时间管理
```tasks
(scheduled on today)OR(due on today)
group by priority
hide tags
```

**预计需要🍅:** 6个
**今日完成题目数量 :**       (每日>3)
```dataviewjs
const pages = dv.pages();
const emoji = "🍅";

// 1. 获取并格式化今天的日期
const today = new Date();
const formatDate = (date) => date.toISOString().split('T')[0];
const todayStr = formatDate(today); // 例如 "2026-01-03"

// 2. 筛选出今天完成的 WORK 番茄钟
const todaysPomodoros = pages.file.lists
  .filter((item) => item?.pomodoro == "WORK")
  .filter((item) => {
    // 检查条目的结束时间是否为今天
    if (item.end && item.end.length >= 10) {
      const itemDateStr = item.end.substring(0, 10);
      return itemDateStr === todayStr;
    }
    return false;
  });

// 3. 统计数量和总时长
let count = 0;
let totalMinutes = 0;

for (let item of todaysPomodoros) {
  count++;
  if (item.duration) {
    totalMinutes += item.duration.as("minutes");
  }
}

// 4. 转换为小时和分钟格式
const hours = Math.floor(totalMinutes / 60);
const minutes = Math.round(totalMinutes % 60);

// 5. 以清晰的方式呈现结果
dv.header(3, `今日番茄钟统计`);
dv.paragraph(`**日期：** ${todayStr}`);
dv.paragraph(`**完成数量：** ${emoji.repeat(count) || "0"} (共 **${count}** 个)`);
dv.paragraph(`**总时长：** ${hours}小时${minutes}分钟`);
```
# 昨天没有完成的

```tasks
not done
(scheduled on last day)OR(due on last day)
group by priority
short mode
hide tags
```

--- 

# 紧急并且重要

==按照截止日期排序==

```tasks
not done
priority is above medium
sort by due
group by due
due in or before next three days
hide tags
show due date
```


# 紧急但不重要

==加快速度, 偷工减料地做==
==按照截止日期排序== 
```tasks
not done
priority is below high
sort by due date
(due in one day )OR( due yesterday)OR(due in two days)OR(due in three days)
group by due
hide tags
```


# 重要但不紧急

==有计划地做, 长期地做==
==已经计划, 按照**计划时间**排序==
```tasks
not done
(priority is above medium)OR(priority is none)
short mode
sort by priority
group by scheduled
due after three days
hide tags
has scheduled date
```

==未计划, 按照重要性排序==
```tasks
not done
(priority is above medium)OR(priority is medium)
short mode
sort by priority
group by priority
due after three days
hide tags
no scheduled date
```

# 不重要且不紧急

==用零碎时间做==
```tasks
not done
priority is below medium
short mode
sort by due date
due after three days
hide tags
group by priority
```

