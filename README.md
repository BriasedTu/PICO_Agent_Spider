# PICO_Agent_Spider
一些爬虫代码，用来爬取部分医疗网站的数据并处理，目的为训练PICO智能体


目前本仓库包含了:
- 美国糖尿病协会[(ADA)](./PICO_Agent/AmericanDiabetesAssociation),
- 美国心脏协会[(AHA)](./PICO_Agent/AmercianHeartAssociation),
- 安大略癌症护理中心,英国国家医疗保健优化研究所,世界卫生组织[(CCO,NICE,WHO)](./PICO_Agent/PubMed),
- 美国疾病控制与预防中心[(CDC)](./PICO_Agent/CDC), 
- 美国感染性疾病学会[(IDSN)](./New_PICO_Agent/IDSN),
- 苏格兰校际指南网络[(SIGN)](./New_PICO_Agent/SIGN)
- [GREADPRO](./New_PICO_Agent/GREADPRO)

的爬虫，md转换和数据清洗代码。
由于仓库容量限制，大部分爬取结果没有上传。~~此仓库中可以直接调用的爬取结果主要为GREADPRO网站的内容，其以json格式存储在[GREADPRO_GuidelineData](./New_PICO_Agent/GREADPRO/guidelines_data)中。~~(由于论文还在撰写阶段，数据库暂时无法公开)

大部分代码为测试用，无法直接运行。
