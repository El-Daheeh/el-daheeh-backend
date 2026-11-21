# El-Daheeh Backend — End-to-End Test Results
Run: 2026-11-22 (Africa/Cairo), against live server.py on :8791 calling the REAL router (router.py).
Server system prompt carries the course context (Data Warehousing / Medallion), so Bronze/Silver/Gold = the layers.

## Test أ: «اعمل لي عشر أسئلة عن gold و silver و bronze»
- HTTP status: 200 | ok: True | task: quiz | agent: ❓ [وكيل مولِّد الأسئلة] | model: GPT-OSS 120B (Groq)
- Question count: 10 — the model returned the questions as a Markdown table (rows 1–10 below), verified by counting the table rows; every question is about the Medallion layers (Bronze/Silver/Gold), not the metals.

### Full response text

**عشر أسئلة اختبارية حول طبقات Medallion (Bronze – Silver – Gold) في مستودعات البيانات**

| رقم السؤال | السؤال | نوع السؤال | ملاحظات (الإجابة) |
|-----------|--------|------------|-------------------|
| 1 | ما هو الهدف الأساسي لطبقة **Bronze** في بنية Medallion؟ | اختيار من متعدد | **أ)** تخزين البيانات الخام (raw) كما وصلتها من المصدر دون أي تحويل. |
| 2 | أي من العبارات التالية تصف بشكل صحيح ما يتم إجراؤه على البيانات في طبقة **Silver**؟ | اختيار من متعدد | **ب)** تنظيف، تنقية، وتطبيع البيانات (deduplication, filtering, type casting) مع الحفاظ على تاريخ التغيّر (historization). |
| 3 | لماذا تُستخدم طبقة **Gold** في Medallion؟ اختر الإجابة الصحيحة. | اختيار من متعدد | **ج)** تقديم نماذج تجارية جاهزة (aggregations, KPIs, dimensional tables) لدعم التحليل والتقارير. |
| 4 | أي من الأدوات أو التقنيات التالية يُفضَّل استخدامها لإنشاء طبقة **Bronze** في بيئة Azure Databricks أو Snowflake؟ | إجابة قصيرة | عادةً يتم استعمال **Delta Lake** أو **Parquet** مع **Auto‑loader** (Auto‑ingest) لتخزين البيانات الخام. |
| 5 | في سياق إدارة الجودة، ما هو الفرق الرئيسي بين **Data Validation** في Bronze و **Data Quality Checks** في Silver؟ | إجابة مفتوحة | Bronze: التحقق من صحة الصيغة (schema) فقط؛ Silver: قواعد جودة شاملة (null checks, range checks, referential integrity). |
| 6 | أي من الخصائص التالية يجب أن تتوفر في جداول **Gold** لتسهيل استهلاكها في Power BI؟ | اختيار من متعدد | **د)** أن تكون مُعَرَّفة على شكل **Star Schema** (Fact + Dimension) مع مفاتيح بسيطة ومحددة. |
| 7 | صِف مثالاً عملياً لتحويل بيانات مبيعات من Bronze إلى Silver (اذكر خطوة واحدة على الأقل). | إجابة مفتوحة | مثال: **إزالة السجلات المكررة** (deduplication) بناءً على معرف الفاتورة وتوحيد تنسيق تاريخ البيع إلى `yyyy‑MM‑dd`. |
| 8 | ما هو مفهوم **Slowly Changing Dimension (SCD)** وأي طبقة يُطبّق عادةً؟ | اختيار من متعدد | **C)** يُطبق في طبقة **Silver** (أو أحيانًا Gold) لتتبع التغيّر التاريخي للأبعاد. |
| 9 | إذا كان لديك جدول **Bronze** يحتوي على 500 مليون سجل، وما هو الإجراء الموصى به قبل ترحيله إلى **Silver** لتقليل الحجم؟ | إجابة مفتوحة | **تقسيم (partitioning)**، **ضغط (compression)**، وإزالة السجلات غير الصالحة أو المكررة. |
| 10 | كيف يمكن ربط طبقة **Gold** مع Power BI لتحديث التقارير بشكل **incremental**؟ | إجابة مفتوحة | إنشاء **جدول فاصل زمني (incremental load table)** في Gold مع عمود **watermark** (مثلاً `last_modified_timestamp`) ثم ضبط **Power BI Dataflow** أو **DirectQuery** لاستخدام هذا الـ watermark لتحديث البيانات فقط. |

---

### ملاحظات للمعلم / الممتحن
- **درجة السؤال**: يمكنك إعطاء كل سؤال نقطة واحدة أو تعديل الدرجات حسب صعوبة السؤال.
- **طريقة التصحيح**: يفضل توفير جدول إجابيات (Answer Key) للخيارات المتعددة وتحديد المعايير للإجابات المفتوحة.
- **تكامل مع Power BI**: استخدم الأسئلة 6، 9 و10 لتقييم قدرة الطالب على ربط الطبقات بالـ BI وتطبيق أفضل الممارسات.

## Test ب: «اشرح لي الأسئلة»
- HTTP status: 200 | ok: True | task: explain | agent: 💡 [وكيل الشرح والفهم] | model: Gemini Flash Lite

### Full response text

أهلاً بك في منصة «الدحيح» التعليمية! 

بما أنك لم ترفق الأسئلة المحددة، سأفترض أنك تقصد **الأسئلة الشائعة في اختبارات مقرر مستودعات البيانات (Data Warehousing)** والتي تغطي المفاهيم الأساسية التي ندرسها هنا: معمارية الميداليون (Medallion Architecture: Bronze, Silver, Gold)، تصميم قواعد البيانات (Star Schema)، وأدوات العرض مثل (Power BI).

إليك شرحاً عملياً ومباشراً لأهم 3 مفاهيم تأتي غالباً في شكل أسئلة كويز في هذا المقرر:

---

### 1. طبقات معمارية الميداليون (Medallion Architecture)
السؤال المتكرر غالباً يكون: *ما الفرق بين Bronze و Silver و Gold؟*
* **طبقة البرونز (Bronze Layer):**
  * **الفكرة:** هي نقطة البخار الأولى (Raw Data). البيانات تُخزن كما هي تماماً من المصدر (Raw)، بدون أي تنظيف أو تعديل (JSON, CSV, DB dumps).
  * **الهدف:** الاحتفاظ بنسخة مطابقة للأصل للرجوع إليها عند الحاجة أو حدوث خطأ في المعالجة.
* **طبقة الفضة (Silver Layer):**
  * **الفكرة:** مرحلة التنظيف والفلترة (Cleaned & Conformed). نقوم بإزالة التكرارات، تصحيح الأخطاء الإملائية، توحيد صيغ التواريخ، وربط الجداول ببعضها.
  * **الهدف:** توفير بيانات موثوقة وجاهزة للتحليل الهندسي أو بناء النماذج.
* **طبقة الذهب (Gold Layer):**
  * **الفكرة:** مرحلة الجاهزية للأعمال (Business-Level / Aggregated). البيانات هنا تكون مهيأة على شكل نماذج تحليلية (مثل Star Schema) وجاهزة لربطها مباشرة بأدوات الـ BI.
  * **الهدف:** استخراج التقارير ودعم اتخاذ القرار بأسرع أداء ممكن.

---

### 2. تصميم النجمة (Star Schema)
السؤال المتكرر: *ما هي مكونات الـ Star Schema ولماذا تُستخدم؟*
* **المكونات:** 
  * **جدول الحقائق (Fact Table):** يوجد في المنتصف، ويحتوي على المقاييس الرقمية القابلة للقياس (مثل: المبيعات، الكميات، الأرباح) بالإضافة إلى مفاتيح أجنبية.
  * **جداول الأبعاد (Dimension Tables):** تحيط بجدول الحقائق، وتحوي التفاصيل الوصفية (مثل: اسم الزميِن، تصنيف المنتج، فرع المتجر، التاريخ).
* **لماذا تُستخدم؟** لتقليل عمليات الـ Joins المعقدة، وتسريع عمليات الاستعلام (Queries) مقارنة بقواعد البيانات العلائقية العادية (OLTP).

---

### 3. الربط مع Power BI
السؤال المتكرر: *من أين يأخذ Power BI بياناته في هذه المعمارية؟*
* **الإجابة باختصار:** Power BI يتصل مباشرة بـ **طبقة الذهب (Gold Layer)**؛ لأن البيانات هناك تكون نظيفة، مُجمّعة

## Test ج: «عايز خطة مذاكرة»
- HTTP status: 200 | ok: True | task: plan | agent: 📅 [وكيل مخطط المذاكرة] | model: Nemotron 3 Ultra 550B (OR)

### Full response text

# خطة مذاكرة افتراضية لمقرر **Data Warehousing**  
*(Medallion Architecture – Bronze / Silver / Gold – Star Schema – Power BI)*  

> **افتراضات الخطة**  
> 1. لديك **أسبوعان** قبل الامتحان/الكويز.  
> 2. تستطيع تخصيص **2–3 ساعات/يوم** (إجمالي 30–40 ساعة).  
> 3. تعرف أساسيات SQL وPython/Pandas، وإلا أضف 3–4 ساعات للمراجعة السريعة.  
> 4. المنصة مستخدمة: **Databricks / Azure Synapse / Fabric** (المفاهيم واحدة).  
> 5. الهدف: **فهم المفاهيم + حل أسئلة كويز عملية** (وليس بناء مشروع كامل).

---

## 📅 الأسبوع الأول – الأساسيات وطبقة **Bronze → Silver**

| اليوم | المحور | المهام العملية (✅ = تم) | المخرج المستهدف |
|------|--------|------------------------|----------------|
| **1** | **مفاهيم DW & Medallion** | □ فيديو 30 د (Kimball vs Inmon)  □ رسم مخطط طبقات Medallion يدويًا  □ تلخيص فروق Bronze/Silver/Gold في ورقة واحدة | تعريف كل طبقة وسبب وجودها |
| **2** | **Bronze – Raw Ingestion** | □ قراءة CSV/JSON/Parquet إلى Delta Table  □ تطبيق *Append only* + *Schema evolution*  □ تجربة `AUTOMATIC COMPACTION` | كود Notebook يملأ جدول Bronze |
| **3** | **Silver – Cleansing & Conforming** | □ إزالة التكرارات (`dropDuplicates`)  □ توحيد التواريخ/العملات  □ تطبيق **Slowly Changing Dimensions (SCD Type 1 & 2)** على جدول عميل  □ توثيق Data Quality Rules في Data Contract | جداول Silver نظيفة + SCD يعمل |
| **4** | **نمذجة Star Schema** | □ رسم ERD يدويًا لمتجر مبيعات (FactSales + DimDate, DimProduct, DimCustomer, DimStore)  □ تحويل جداول Silver إلى نموذج نجمي (Surrogate Keys, FK)  □ مقارنة Snowflake vs Star | مخطط Star Schema جاهز للتنفيذ |
| **5** | **Gold – Aggregations & Business Views** | □ إنشاء جداول تجميعية: `MonthlySales`, `TopProducts`, `CustomerLTV`  □ تطبيق *Partitioning* على `YearMonth` + *Z-Order* على `ProductKey`  □ اختبار أداء استعلام نموذجي (`EXPLAIN`) | طبقة Gold محسّنة للتحليل |
| **6** | **Data Quality & Testing** | □ كتابة Great Expectations / dbt tests للـ Null PK، نطاق التواريخ، مرجعية FK  □ تشغيل CI/CD pipeline بسيط (GitHub Actions) | اختبارات آلية تمنع كسر البيانات |
| **7** | **مراجعة أسبوعية + كويز تجريبي** | □ حل 15 سؤال MCQ من بنك الأسئلة (انظر أسفل)  □ تدوين الأخطاء في «بطاقات خطرة» (Anki/Notion) | قائمة نقاط ضعف للتركيز الأسبوع الثاني |

---

## 📅 الأسبوع الثاني – **Power BI** + محاكاة امتحان

| اليوم | المحور | المهام العملية | المخرج |
|------|--------|--------------|--------|
| **8** | **Power BI – Connection & Model** | □ ربط Power BI بـ Gold (DirectQuery vs Import)  □ بناء علاقات Star Schema داخل Power BI  □ إعداد *Calculation Groups* للـ Time Intelligence | نموذج BI نظيف |
| **9** | **DAX Patterns** | □ Measures: `Total Sales`, `YoY%`, `Running Total`, `TopN SKU`  □ تطبيق `USERELATIONSHIP` لتحليل الشحن vs الطلب  □ تحسين الأداء بـ `DEFINE MEASURE` في DAX Studio | 10 Measures جاهزة للكويز |
| **10** | **Row-Level Security & Deployment** | □ تطبيق RLS على `DimStore[Region]`  □ نشر للـ Power BI Service + إعداد *Incremental Refresh* | تقرير آمن وقابل للجدولة |
| **11** | **Performance Tuning** | □ تشغيل *Performance Analyzer*  □ تقليل Cardinality، إزالة أعمدة غير مستخدمة  □ مقارنة Import vs DirectQuery على 10M صف | تقرير أداء موثق |
| **12** | **محاكاة كويز كاملة (30 د)** | □ 25 سؤال: 10 Medallion/Star، 10 DAX/Modeling، 5 Best Practices  □ تصحيح ذاتي + مراجعة كل خطأ | درجة ≥ 85% |
| **13** | **مراجعة «البطاقات الخطرة»** | □ إعادة قراءة الملخصات، إعادة كتابة الكود الحرج من الذاكرة | تثبيت المعلومة |
| **14** | **يوم الامتحان / الكويز النهائي** | □ نوم جيد، مراجعة ورقة الغش (Cheat-sheet) صفحة واحدة | ثقة وجاهزية |

---

## 🎯 بنك أسئلة تدريبي (نموذج 15 سؤال – اليوم 7)

| # | السؤال | نوع |
|---|---------|-----|
| 1 | ما الفرق الجوهري بين **Bronze** و **Silver** من ناحية *Schema Enforcement*؟ | MCQ |
| 2 | في SCD Type 2، أي عمود يُستخدم عادةً لتحديد الصف الحالي؟ | MCQ |
| 3 | لماذا نفضل **Surrogate Key** على Natural Key في جداول الأبعاد؟ | MCQ |
| 4 | ما تأثير `Z-ORDER BY (ProductKey)` على استعلام `WHERE ProductKey = 10`؟ | MCQ |
| 5 | عند تصميم Fact Table، ماذا يعني *Additivity*؟ | MCQ |
| 6 | اكتب DAX لـ **Year-To-Date Sales** باستخدام `CALCULATE` و `DATESYTD`. | Code |
| 7 | كيف تمنع مستخدمًا في Power BI من رؤية بيانات منطقة «East» فقط؟ | MCQ |
| 8 | ما الفرق بين **Incremental Refresh** و **DirectQuery** من ناحية مصدر البيانات؟ | MCQ |
| 9 | في Medallion، أين يُطبق *Data Contract* عادةً؟ | MCQ |
| 10 | ما سبب استخدام `GENERATE` في إنشاء `DimDate` بدلاً من تحميل ملف CSV؟ | MCQ |
| 11 | كيف تتعامل مع **Late Arriving Dimensions** في طبقة Silver؟ | Short Answer |
| 12 | ما أفضل ممارسة لتقسيم (Partition) جدول حقائق شهري الحجم 500M صف؟ | MCQ |
| 13 | اكتب استعلام SQL لإنشاء `FactSales` من جداول Silver مع Surrogate Keys. | Code |
| 14 | ماذا يعني «Chasm Trap» في Star Schema وكيف تحله؟ | MCQ |
| 15 | ما مقياس أداء (KPI) تراقبه يوميًا لصحة Pipeline Medallion؟ | Short Answer |

> **نصيحة**: حول كل سؤال أخطأت فيه إلى «بطاقة خطرة» وراجعها يوم 13.

---

## 🗂️ ورقة غش (Cheat-sheet) صفحة واحدة – للطباعة يوم 14

|层 | الهدف | تقنيات رئيسية | فخاخ شائعة |
|---|-------|----------------|-------------|
| **Bronze** | هبوط خام (Landing) | Append-only, Schema Evolution, Auto Compaction | عدم حفظ نسخة خام، حذف ملفات المصدر |
| **Silver** | تنظيف + توحيد + SCD | Dedup, Type 1/2 SCD, Data Contracts, Great Expectations | مفتاح طبيعي متغير، نسيان `mergeSchema` |
| **Gold** | تجميعات تجارية | Star Schema, Partition + Z-Order, Materialized Views | Over-aggregation (تفقد التفاصيل)، عدم تحديث الإحصائيات |
| **Power BI** | عرض + تحليل | Import/DirectQuery, RLS, Incremental Refresh, DAX Patterns | نمذجة Snowflake داخل BI، Measures غير محسّنة |

---

## ⚙️ كيف تخصص الخطة لو وضعك مختلف؟

| متغير | تعديل مقترح |
|--------|-------------|
| **أسبوع واحد فقط** | احذف الأيام 2، 6، 10، 11؛ ركز على: Medallion概念 + Star Schema + DAX الأساسي + كويز واحد كامل. |
| **لا تعرف SQL** | أضف اليوم 0: «SQL أساسي للـ DW» (CTE, Window Functions, MERGE). |
| **بيئة Snowflake/BigQuery** | استبدل Delta/Parquet بـ Micro-partitions/Clustering، المفاهيم واحدة. |
| **هدفك مشروع لا كويز** | زد الأيام 3، 5، 9، 11 لتغطي CI/CD، Data Catalog، Monitoring. |

---

### ✅ خطوة التالية منك
1. حدّد **موعد الامتحان/الكويز** وعدد الساعات المتاحة يوميًا.  
2. لو تختلف افتراضاتي، قل لي وأعدل الخطة فورًا.  
3. ابدأ باليوم 1 الآن: شاهد فيديو 30 د وارسم مخطط Medallion يدويًا.  

بالتوفيق! 🚀

---

## Verification notes

- **Page validity:** edited index.html — tags balanced (script/body/html 1/1, div 17/17); the script block passes `node --check` (JS SYNTAX OK).
- **Page + backend together:** site served locally on :8792 (HTTP 200, 14,582 bytes) while the backend answered on :8791.
- **Fallback (backend down):** backend was stopped and `curl http://localhost:8791/health` → connection refused, i.e. the page's `fetch` rejects and the `catch` in `send()` calls the original canned `reply(v)` — confirmed by code inspection (index.html lines 199–201; `reply()` itself untouched). Backend was then restarted and /health is ok again.
- **Model variance note:** free providers fluctuate — in an earlier run the same quiz request was served by Qwen 3.8 27B and one explain request hit a transient 502 (all candidates down that minute); the router's fallback chain is what carried the final run. In the final run above, the plan request fell back past Gemini to Nemotron 3 Ultra and still returned a full plan.
