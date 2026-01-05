# 1.1文档

你是一名python开发专家，阅读以下文档完成任务：

进入命令行会呈现两个进入界面选项，分别为增加行为界面以及记录行为界面：

### 1.增加行为界面（add_**behavior.py**）

用户进入该界面，只需要输入行为习惯等级（level）和行为习惯名称（**behavior**），其余信息（分数和精力消耗等）确定等级后，自动填充

下面是需实现的相关数据结构体：

```json
{ //用于存储行为信息
name:string   //行为名称,唯一值
level:struct  //行为等级，为结构体
category:string //类别
start_time:string  //行为起始时间
end_time:string  //行为结束时间
date:string  //日期
behavior**_**score:int   //行为得分
mood_score:int    //心情得分
}
```

```json
{ // 用于存储等级信息
S:{//高精力消耗、高长期回报的行为（如深度工作、高强度锻炼）
base_score:5    //基础得分
energy_cost:5  //精力消耗
level_weight:1  //等级权重系数
chain_weight:1  //连锁权重系数
}
A:{//中等精力消耗、有长期回报的行为（如学习、阅读）
base_score:3    //基础得分
energy_cost:3   //精力消耗
level_weight:1  //等级权重系数
chain_weight:1  //连锁权重系数
}
B:{//低精力消耗、维持性行为（如整理、复习）
base_score:1    //基础得分
energy_cost:1   //精力消耗
level_weight:1  //等级权重系数
chain_weight:1  //连锁权重系数
}
C:{//低精力消耗、即时快乐但长期有害的行为（如无目的刷手机）
base_score:-3    //基础得分
energy_cost:3   //精力消耗
level_weight:1  //等级权重系数
chain_weight:1  //连锁权重系数
}
D:{//高精力消耗、长期有害的行为（如熬夜、暴饮暴食）
base_score:-5    //基础得分
energy_cost:5   //精力消耗
level_weight:1  //等级权重系数
chain_weight:1  //连锁权重系数
}
}
```

```json
{//用于存储用户所有信息
behavior_list = []  //存储所有行为信息
behavior_day_list = []  //存储当日行为信息
total_score = int  //总得分
day_score = int   //当日得分
history_score = [{date:string;score:int}]  //历史得分列表
total_energy = int  //总精力
day_energy = int   //当日精力剩余
day_energy_cost = int //当日精力消耗
history_energy_cost = [{date:string;cost:int}] //历史精力消耗
}
```

```json
//全局参数配置
{
per_time = 1  //每几分钟 用于计算得分   得分公式 = 基础得分/per_time
}

```

### 2.记录行为界面(record_**behavior.py**)

记录行为的时候，要先输入等级，就会先显示该等级各个行为，再选择对应行为，最后输入行为进行时长，得出该行为的得分