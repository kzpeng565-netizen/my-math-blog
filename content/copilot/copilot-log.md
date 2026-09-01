
2026-09-01T11:00:02.020Z INFO Copilot Plus: Initializ









ing semantic index event listeners
2026-09-01T11:00:02.021Z INFO VaultDataManager: Initializing with vault event listeners
2026-09-01T11:00:02.022Z INFO Setting model to deepseek-v4-pro|deepseek
2026-09-01T11:00:02.596Z INFO Loaded existing chunked semantic index database from disk.
2026-09-01T11:00:04.662Z INFO [Projects] Initializing ProjectFileManager
2026-09-01T11:00:04.662Z INFO Initializing SystemPromptManager
2026-09-01T11:00:04.662Z INFO No legacy userSystemPrompt to migrate
2026-09-01T11:02:12.943Z INFO First ping attempt failed, retrying with CORS enabled.
2026-09-01T11:02:12.945Z INFO safeFetch request
2026-09-01T11:02:16.938Z INFO safeFetch request
2026-09-01T11:02:21.961Z ERROR \nwithout CORS Error: Request was aborted.\nwith CORS Error: Request was aborted.\nError: \nwithout CORS Error: Request was aborted.\nwith CORS Error: Request was aborted.\n    at cs.ping (plugin:copilot:624:32)\n    at async V (plugin:copilot:2588:4393)
2026-09-01T11:02:47.672Z INFO Setting model to deepseek-v4-pro|deepseek
2026-09-01T11:03:10.552Z INFO Enabling Responses API for GPT-5 model: gpt-5.6-sol (3rd party (openai-format))
2026-09-01T11:03:10.552Z INFO Enabling Responses API for GPT-5 model: gpt-5.6-sol (3rd party (openai-format))
2026-09-01T11:03:10.552Z INFO Chat model set with Responses API for GPT-5: gpt-5.6-sol
2026-09-01T11:03:10.552Z INFO Chat model set with Responses API for GPT-5: gpt-5.6-sol
2026-09-01T11:03:10.552Z INFO Setting model to gpt-5.6-sol|3rd party (openai-format)
2026-09-01T11:03:10.552Z INFO Setting model to gpt-5.6-sol|3rd party (openai-format)
2026-09-01T11:03:18.142Z INFO [ChatManager] Sending message: "测试"
2026-09-01T11:03:18.142Z INFO [MessageRepository] Added message with ID: msg-1788260598128-p7k7gykl3
2026-09-01T11:03:18.142Z INFO [UserMemoryManager] Recent Conversations file not found, skipping memory load
2026-09-01T11:03:18.142Z INFO [UserMemoryManager] Saved Memories file not found, skipping saved memory load
2026-09-01T11:03:18.144Z INFO [ContextManager] Processing context for message msg-1788260598128-p7k7gykl3
2026-09-01T11:03:18.156Z INFO [ContextManager] Successfully processed context for message msg-1788260598128-p7k7gykl3
2026-09-01T11:03:18.156Z INFO [PromptContextEngine] Built envelope for message:msg-1788260598128-p7k7gykl3 {"L1_SYSTEM":"18632c192275773ea338b5ae2cd96c5ae3bf2b48e4db3489f4d59868ad491ad2","L2_PREVIOUS":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","L3_TURN":"a03799178ae56ab9bde026b31c427401d5e7bfd0a727272b9750128aae9e86a8","L4_STRIP":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","L5_USER":"6aa8f49cc992dfd75a114269ed26de0ad6d4e7d7a70d9c8afb3d7a57a88a73ed"}
2026-09-01T11:03:18.156Z INFO [MessageRepository] Updated processed text for message msg-1788260598128-p7k7gykl3
2026-09-01T11:03:18.156Z INFO [ChatManager] Successfully sent message msg-1788260598128-p7k7gykl3
2026-09-01T11:03:18.183Z INFO [ChatPersistenceManager] Created new chat file: copilot/copilot-conversations/测试@20260901_190318.md
2026-09-01T11:03:18.185Z INFO Step 0: Initial user message:\n 测试
2026-09-01T11:03:18.185Z INFO [ThinkBlockStreamer] Created with excludeThinking=false
2026-09-01T11:03:18.185Z INFO [LLMChainRunner] Using envelope-based context
2026-09-01T11:03:18.186Z INFO Final Request to AI:\n [{"role":"system","content":"You are Obsidian Copilot, a helpful assistant that integrates AI to Obsidian note-taking.\n  1. Never mention that you do not have access to something. Always rely on the user provided context.\n  2. Always answer to the best of your knowledge. If you are unsure about something, say so and ask the user to provide more context.\n  3. If the user mentions \"note\", it most likely means an Obsidian note in the vault, not the generic meaning of a note.\n  4. If the user mentions \"@vault\", it means the user wants you to search the Obsidian vault for information relevant to the query. The search results will be provided to you in the context along with the user query, read it carefully and answer the question based on the information provided. If there's no relevant information in the vault, just say so.\n  5. If the user mentions any other tool with the @ symbol, check the context for their results. If nothing is found, just ignore the @ symbol in the query.\n  6. Always use $'s instead of \\[ etc. for LaTeX equations.\n  7. When showing note titles, use [[title]] format and do not wrap them in ` `.\n  8. When showing **Obsidian internal** image links, use ![[link]] format and do not wrap them in ` `.\n  9. When showing **web** image links, use ![link](url) format and do not wrap them in ` `.\n  10. When generating a table, format as github markdown tables, however, for table headings, immediately add ' |' after the table heading.\n  11. Always respond in the language of the user's query.\n  12. Do NOT mention the additional context provided such as getCurrentTime and getTimeRangeMs if it's irrelevant to the user message.\n  13. If the user mentions \"tags\", it most likely means tags in Obsidian note properties.\n  14. YouTube URLs: If the user provides YouTube URLs in their message, transcriptions will be automatically fetched and provided to you. You don't need to do anything special - just use the transcription content if available.\n  15. For markdown lists, always use '- ' (hyphen followed by exactly one space) for bullet points, with no leading spaces before the hyphen. Never use '*' (asterisk) for bullets."},{"role":"user","content":[{"type":"text","text":"&lt;active_note&gt;\n&lt;title&gt;ToDo-已经规划好的任务&lt;/title&gt;\n&lt;path&gt;非笔记内容/任务计划/ToDo-已经规划好的任务.md&lt;/path&gt;\n&lt;ctime&gt;2026-09-01T08:52:45.081Z&lt;/ctime&gt;\n&lt;mtime&gt;2026-09-01T08:52:34.173Z&lt;/mtime&gt;\n&lt;content&gt;\n#时间管理 \n\n**目前我已经放假*** \n⏳代表 scheduled day；📅代表 deadline；1 🍅 = 40 分钟 ; 🔁代表recurring 例如- [ ] #task a 🔁 every day 📅 2026-07-24 \n\n**周六周天不要布置其他任务, 周一下午午休到两点之后可以布置任务, 除了上课前两小时之外, 不需要备课**\n\n# 2026-07-27 假期任务规划\n\n## 1. 数学学习\n\n## 2. 家教授课与备课\n\n\n\n\n# 2026-07-31 假期任务规划\n\n## 1. 数学学习\n\n\n## 2. 生活与设备\n\n\n\n\n\n- [ ] #task 做完GTM259 §2.1选择的习题 [🍅:: 2/4] 🔼 ⏳ 2026-09-01 📅 2026-09-01 ^73e1e9cd\n\n- [ ] #task 回看GTM259 Ch.1 §1.1–1.2 [🍅:: 0/1] 🔼 ⏳ 2026-09-01 ^b24fc7b0\n\n\n# 2026-08-09 假期任务规划\n\n## 1. 健康训练\n\n- [ ] #task 第1–4周膝盖恢复期：完成周一低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Monday ⏳ 2026-08-17 ^h26080901\n- [ ] #task 第1–4周膝盖恢复期：完成周二飞机杯行为训练、30秒记录和呼吸/盆底 ⏳ 2026-08-18 [🍅:: 0/1] 🔁 every week on Tuesday ^h26080902\n- [ ] #task 第1–4周膝盖恢复期：完成周三低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Wednesday ⏳ 2026-08-12 ^h26080903\n- [ ] #task 第1–4周膝盖恢复期：完成周四飞机杯行为训练、30秒记录和呼吸/盆底 [🍅:: 0/1] 🔁 every week on Thursday ⏳ 2026-08-13 ^h26080904\n- [ ] #task 第1–4周膝盖恢复期：完成周五低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Friday ⏳ 2026-08-14 ^h26080905\n- [ ] #task 第1–4周膝盖恢复期：完成周六飞机杯训练或双周标准化测试，并做呼吸/盆底 [🍅:: 0/1] 🔁 every week on Saturday ⏳ 2026-08-15 ^h26080906\n- [ ] #task 第1–4周膝盖恢复期：完成周日低膝负荷有氧20分钟、呼吸/盆底和本周记录快看 ⏳ 2026-08-16 [🍅:: 0/1] 🔁 every week on Sunday ^h26080907\n- [ ] #task 每4周完成一次健康训练阶段评估（硬度、控制、焦虑、时间、性兴趣） [🍅:: 0/1] 🔁 every 4 weeks on Sunday ⏳ 2026-08-30 ^h26080908\n\n## 2. 返校后健康维持\n\n- [ ] #task 第5–12周返校阶段：周一力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Monday ⏳ 2026-09-07 ^h26080909\n- [ ] #task 第5–12周返校阶段：周二完成飞机杯训练15分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Tuesday ⏳ 2026-09-08 ^h26080910\n- [ ] #task 第5–12周返校阶段：周三力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Wednesday ⏳ 2026-09-09 ^h26080911\n- [ ] #task 第5–12周返校阶段：周四完成飞机杯训练15分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Thursday ⏳ 2026-09-10 ^h26080912\n- [ ] #task 第5–12周返校阶段：周五力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Friday ⏳ 2026-09-11 ^h26080913\n- [ ] #task 第5–12周返校阶段：周六完成飞机杯训练或双周标准化测试，并做呼吸/盆底 [🍅:: 0/1] 🔁 every week on Saturday ⏳ 2026-09-12 ^h26080914\n- [ ] #task 第5–12周返校阶段：周日完成有氧30分钟、呼吸/盆底和本周记录快看 [🍅:: 0/1] 🔁 every week on Sunday ⏳ 2026-09-06 ^h26080915\n\n&gt; 计划备注：本批次来自 [[非笔记内容/任务计划/健康计划.md]]。第1–4周按膝盖恢复期执行，低膝负荷有氧优先；第5–12周在膝盖基本恢复且可恢复运动后执行。单日专项均按 1 🍅 记录；5分钟呼吸/盆底若单独执行则不估计番茄钟。双周标准化测试替代当周一次飞机杯训练，不额外增加一次训练。\n\n# 2026-08-31 目标模式启动任务\n\n- [ ] #task 学习GTM259 §2.2 Recurrence并重建Poincaré复现证明 [🍅:: 0/5] 🔼 ⏳ 2026-09-03 📅 2026-09-03 ^e260902a\n- [ ] #task 复习抽象代数群论基础与商群同构 [🍅:: 0/5] 🔼 ⏳ 2026-09-02 📅 2026-09-02 ^p260903a\n- [ ] #task 完成GTM259 §2.2习题与证明复述 [🍅:: 0/5] 🔼 ⏳ 2026-09-05 📅 2026-09-05 ^e260903a\n- [ ] #task 复习抽象代数群作用与Sylow定理 [🍅:: 0/3] 🔼 ⏳ 2026-09-04 📅 2026-09-04 ^p260904a\n- [ ] #task 完成抽象代数Sylow定理选题基线 [🍅:: 0/4] 🔼 ⏳ 2026-09-06 📅 2026-09-06 ^a260906a\n\n&gt; 计划备注：本批次来自用户 2026-08-31 对目标模式的直接更正，执行细则见 [[07-概率论教材更正与近期学习启动]]。这些是 GTM259 与抽象代数先行任务；概率论等待真实课堂笔记后再接管，不代表老师已讲到相应内容；真实概率论课堂或作业出现时优先接管同一容量。周末只保留本批次已列出的目标模式学习块，不再叠加其他事项。\n\n\n&lt;/content&gt;\n&lt;/active_note&gt;\n\n---\n\n[User query]:\n\n测试"}]}]
2026-09-01T11:03:29.182Z ERROR [ChatPersistenceManager] Error generating AI topic: Connection error.\nmore message: Failed to fetch\nError: Connection error.\n    at en.makeRequest (plugin:copilot:273:4456)\n    at async eval (plugin:copilot:280:61047)\n    at async Q2 (plugin:copilot:203:24170)\n    at async i (plugin:copilot:202:8726)
2026-09-01T11:03:32.799Z ERROR Error during LLM invocation: Connection error.\nmore message: Failed to fetch
2026-09-01T11:03:32.799Z ERROR Connection error.\nmore message: Failed to fetch
2026-09-01T11:03:32.800Z INFO [MessageRepository] Added message with ID: msg-fdb6d439-84a1-4356-9e7d-f67101fd4926
2026-09-01T11:03:32.800Z INFO Chat memory updated:\n {"turns":2}
2026-09-01T11:03:32.800Z INFO Final AI response (truncated):\n \n&lt;errorChunk&gt;Connection error.\nmore message: Failed to fetch&lt;/errorChunk&gt;
2026-09-01T11:03:32.822Z INFO [ChatPersistenceManager] Updated existing chat file: copilot/copilot-conversations/测试@20260901_190318.md
2026-09-01T11:03:45.822Z ERROR [ChatPersistenceManager] Error generating AI topic: Connection error.\nmore message: Failed to fetch\nError: Connection error.\n    at en.makeRequest (plugin:copilot:273:4456)\n    at async eval (plugin:copilot:280:61047)\n    at async Q2 (plugin:copilot:203:24170)\n    at async i (plugin:copilot:202:8726)
2026-09-01T11:23:24.916Z INFO [ThinkBlockStreamer] Created with excludeThinking=true
2026-09-01T11:23:25.066Z ERROR Error generating response: Copilot Plus license key is not configured. Please enter your license key in the Copilot Plus section at the top of Basic Settings.\nMissingPlusLicenseError: Copilot Plus license key is not configured. Please enter your license key in the Copilot Plus section at the top of Basic Settings.\n    at cs.createModelInstance (plugin:copilot:622:21336)\n    at Crt (plugin:copilot:2313:55137)\n    at eval (plugin:copilot:2313:56792)\n    at eval (plugin:copilot:2313:57986)\n    at async Pe (plugin:copilot:2313:61128)
2026-09-01T11:29:32.656Z INFO [ThinkBlockStreamer] Created with excludeThinking=true
2026-09-01T11:29:32.657Z ERROR Error generating response: Copilot Plus license key is not configured. Please enter your license key in the Copilot Plus section at the top of Basic Settings.\nMissingPlusLicenseError: Copilot Plus license key is not configured. Please enter your license key in the Copilot Plus section at the top of Basic Settings.\n    at cs.createModelInstance (plugin:copilot:622:21336)\n    at Crt (plugin:copilot:2313:55137)\n    at eval (plugin:copilot:2313:56792)\n    at eval (plugin:copilot:2313:57986)\n    at async K (plugin:copilot:2313:61564)
2026-09-01T11:34:39.448Z INFO [ChatManager] Sending message: "请只回复：COPILOT_OK"
2026-09-01T11:34:39.448Z INFO [MessageRepository] Added message with ID: msg-1788262479421-60x8s6urt
2026-09-01T11:34:39.448Z INFO [UserMemoryManager] Recent Conversations file not found, skipping memory load
2026-09-01T11:34:39.448Z INFO [UserMemoryManager] Saved Memories file not found, skipping saved memory load
2026-09-01T11:34:39.453Z INFO [ContextManager] Processing context for message msg-1788262479421-60x8s6urt
2026-09-01T11:34:39.453Z INFO Skipping note 非笔记内容/任务计划/ToDo-已经规划好的任务.md as it was included via custom prompt.
2026-09-01T11:34:39.463Z INFO [ContextManager] Successfully processed context for message msg-1788262479421-60x8s6urt
2026-09-01T11:34:39.464Z INFO [PromptContextEngine] Built envelope for message:msg-1788262479421-60x8s6urt {"L1_SYSTEM":"18632c192275773ea338b5ae2cd96c5ae3bf2b48e4db3489f4d59868ad491ad2","L2_PREVIOUS":"a03799178ae56ab9bde026b31c427401d5e7bfd0a727272b9750128aae9e86a8","L3_TURN":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","L4_STRIP":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","L5_USER":"defadd77e85a34a40d3b2c0019953961cfe18bceab0e5fbd98f919a845555ffb"}
2026-09-01T11:34:39.464Z INFO [MessageRepository] Updated processed text for message msg-1788262479421-60x8s6urt
2026-09-01T11:34:39.464Z INFO [ChatManager] Successfully sent message msg-1788262479421-60x8s6urt
2026-09-01T11:34:39.509Z INFO [ChatPersistenceManager] Updated existing chat file: copilot/copilot-conversations/测试@20260901_190318.md
2026-09-01T11:34:39.511Z INFO Step 0: Initial user message:\n 请只回复：COPILOT_OK
2026-09-01T11:34:39.511Z INFO [ThinkBlockStreamer] Created with excludeThinking=false
2026-09-01T11:34:39.511Z INFO [LLMChainRunner] Using envelope-based context
2026-09-01T11:34:39.512Z INFO Final Request to AI:\n [{"role":"system","content":"You are Obsidian Copilot, a helpful assistant that integrates AI to Obsidian note-taking.\n  1. Never mention that you do not have access to something. Always rely on the user provided context.\n  2. Always answer to the best of your knowledge. If you are unsure about something, say so and ask the user to provide more context.\n  3. If the user mentions \"note\", it most likely means an Obsidian note in the vault, not the generic meaning of a note.\n  4. If the user mentions \"@vault\", it means the user wants you to search the Obsidian vault for information relevant to the query. The search results will be provided to you in the context along with the user query, read it carefully and answer the question based on the information provided. If there's no relevant information in the vault, just say so.\n  5. If the user mentions any other tool with the @ symbol, check the context for their results. If nothing is found, just ignore the @ symbol in the query.\n  6. Always use $'s instead of \\[ etc. for LaTeX equations.\n  7. When showing note titles, use [[title]] format and do not wrap them in ` `.\n  8. When showing **Obsidian internal** image links, use ![[link]] format and do not wrap them in ` `.\n  9. When showing **web** image links, use ![link](url) format and do not wrap them in ` `.\n  10. When generating a table, format as github markdown tables, however, for table headings, immediately add ' |' after the table heading.\n  11. Always respond in the language of the user's query.\n  12. Do NOT mention the additional context provided such as getCurrentTime and getTimeRangeMs if it's irrelevant to the user message.\n  13. If the user mentions \"tags\", it most likely means tags in Obsidian note properties.\n  14. YouTube URLs: If the user provides YouTube URLs in their message, transcriptions will be automatically fetched and provided to you. You don't need to do anything special - just use the transcription content if available.\n  15. For markdown lists, always use '- ' (hyphen followed by exactly one space) for bullet points, with no leading spaces before the hyphen. Never use '*' (asterisk) for bullets.\n\n## Context Library\n\nThe following notes are available for reference:\n\n&lt;active_note&gt;\n&lt;title&gt;ToDo-已经规划好的任务&lt;/title&gt;\n&lt;path&gt;非笔记内容/任务计划/ToDo-已经规划好的任务.md&lt;/path&gt;\n&lt;ctime&gt;2026-09-01T08:52:45.081Z&lt;/ctime&gt;\n&lt;mtime&gt;2026-09-01T08:52:34.173Z&lt;/mtime&gt;\n&lt;content&gt;\n#时间管理 \n\n**目前我已经放假*** \n⏳代表 scheduled day；📅代表 deadline；1 🍅 = 40 分钟 ; 🔁代表recurring 例如- [ ] #task a 🔁 every day 📅 2026-07-24 \n\n**周六周天不要布置其他任务, 周一下午午休到两点之后可以布置任务, 除了上课前两小时之外, 不需要备课**\n\n# 2026-07-27 假期任务规划\n\n## 1. 数学学习\n\n## 2. 家教授课与备课\n\n\n\n\n# 2026-07-31 假期任务规划\n\n## 1. 数学学习\n\n\n## 2. 生活与设备\n\n\n\n\n\n- [ ] #task 做完GTM259 §2.1选择的习题 [🍅:: 2/4] 🔼 ⏳ 2026-09-01 📅 2026-09-01 ^73e1e9cd\n\n- [ ] #task 回看GTM259 Ch.1 §1.1–1.2 [🍅:: 0/1] 🔼 ⏳ 2026-09-01 ^b24fc7b0\n\n\n# 2026-08-09 假期任务规划\n\n## 1. 健康训练\n\n- [ ] #task 第1–4周膝盖恢复期：完成周一低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Monday ⏳ 2026-08-17 ^h26080901\n- [ ] #task 第1–4周膝盖恢复期：完成周二飞机杯行为训练、30秒记录和呼吸/盆底 ⏳ 2026-08-18 [🍅:: 0/1] 🔁 every week on Tuesday ^h26080902\n- [ ] #task 第1–4周膝盖恢复期：完成周三低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Wednesday ⏳ 2026-08-12 ^h26080903\n- [ ] #task 第1–4周膝盖恢复期：完成周四飞机杯行为训练、30秒记录和呼吸/盆底 [🍅:: 0/1] 🔁 every week on Thursday ⏳ 2026-08-13 ^h26080904\n- [ ] #task 第1–4周膝盖恢复期：完成周五低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Friday ⏳ 2026-08-14 ^h26080905\n- [ ] #task 第1–4周膝盖恢复期：完成周六飞机杯训练或双周标准化测试，并做呼吸/盆底 [🍅:: 0/1] 🔁 every week on Saturday ⏳ 2026-08-15 ^h26080906\n- [ ] #task 第1–4周膝盖恢复期：完成周日低膝负荷有氧20分钟、呼吸/盆底和本周记录快看 ⏳ 2026-08-16 [🍅:: 0/1] 🔁 every week on Sunday ^h26080907\n- [ ] #task 每4周完成一次健康训练阶段评估（硬度、控制、焦虑、时间、性兴趣） [🍅:: 0/1] 🔁 every 4 weeks on Sunday ⏳ 2026-08-30 ^h26080908\n\n## 2. 返校后健康维持\n\n- [ ] #task 第5–12周返校阶段：周一力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Monday ⏳ 2026-09-07 ^h26080909\n- [ ] #task 第5–12周返校阶段：周二完成飞机杯训练15分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Tuesday ⏳ 2026-09-08 ^h26080910\n- [ ] #task 第5–12周返校阶段：周三力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Wednesday ⏳ 2026-09-09 ^h26080911\n- [ ] #task 第5–12周返校阶段：周四完成飞机杯训练15分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Thursday ⏳ 2026-09-10 ^h26080912\n- [ ] #task 第5–12周返校阶段：周五力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Friday ⏳ 2026-09-11 ^h26080913\n- [ ] #task 第5–12周返校阶段：周六完成飞机杯训练或双周标准化测试，并做呼吸/盆底 [🍅:: 0/1] 🔁 every week on Saturday ⏳ 2026-09-12 ^h26080914\n- [ ] #task 第5–12周返校阶段：周日完成有氧30分钟、呼吸/盆底和本周记录快看 [🍅:: 0/1] 🔁 every week on Sunday ⏳ 2026-09-06 ^h26080915\n\n&gt; 计划备注：本批次来自 [[非笔记内容/任务计划/健康计划.md]]。第1–4周按膝盖恢复期执行，低膝负荷有氧优先；第5–12周在膝盖基本恢复且可恢复运动后执行。单日专项均按 1 🍅 记录；5分钟呼吸/盆底若单独执行则不估计番茄钟。双周标准化测试替代当周一次飞机杯训练，不额外增加一次训练。\n\n# 2026-08-31 目标模式启动任务\n\n- [ ] #task 学习GTM259 §2.2 Recurrence并重建Poincaré复现证明 [🍅:: 0/5] 🔼 ⏳ 2026-09-03 📅 2026-09-03 ^e260902a\n- [ ] #task 复习抽象代数群论基础与商群同构 [🍅:: 0/5] 🔼 ⏳ 2026-09-02 📅 2026-09-02 ^p260903a\n- [ ] #task 完成GTM259 §2.2习题与证明复述 [🍅:: 0/5] 🔼 ⏳ 2026-09-05 📅 2026-09-05 ^e260903a\n- [ ] #task 复习抽象代数群作用与Sylow定理 [🍅:: 0/3] 🔼 ⏳ 2026-09-04 📅 2026-09-04 ^p260904a\n- [ ] #task 完成抽象代数Sylow定理选题基线 [🍅:: 0/4] 🔼 ⏳ 2026-09-06 📅 2026-09-06 ^a260906a\n\n&gt; 计划备注：本批次来自用户 2026-08-31 对目标模式的直接更正，执行细则见 [[07-概率论教材更正与近期学习启动]]。这些是 GTM259 与抽象代数先行任务；概率论等待真实课堂笔记后再接管，不代表老师已讲到相应内容；真实概率论课堂或作业出现时优先接管同一容量。周末只保留本批次已列出的目标模式学习块，不再叠加其他事项。\n\n\n&lt;/content&gt;\n&lt;/active_note&gt;"},{"role":"user","content":"测试"},{"role":"assistant","content":"\n&lt;errorChunk&gt;Connection error.\nmore message: Failed to fetch&lt;/errorChunk&gt;"},{"role":"user","content":[{"type":"text","text":"请只回复：COPILOT_OK"}]}]
2026-09-01T11:34:53.350Z ERROR [ChatPersistenceManager] Error generating AI topic: Connection error.\nmore message: Failed to fetch\nError: Connection error.\n    at en.makeRequest (plugin:copilot:273:4456)\n    at async eval (plugin:copilot:280:61047)\n    at async Q2 (plugin:copilot:203:24170)\n    at async i (plugin:copilot:202:8726)
2026-09-01T11:34:55.421Z ERROR Error during LLM invocation: Connection error.\nmore message: Failed to fetch
2026-09-01T11:34:55.421Z ERROR Connection error.\nmore message: Failed to fetch
2026-09-01T11:34:55.422Z INFO [MessageRepository] Added message with ID: msg-f5264190-8990-4dfa-a616-302741c3bad9
2026-09-01T11:34:55.422Z INFO Chat memory updated:\n {"turns":4}
2026-09-01T11:34:55.422Z INFO Final AI response (truncated):\n \n&lt;errorChunk&gt;Connection error.\nmore message: Failed to fetch&lt;/errorChunk&gt;
2026-09-01T11:34:55.475Z INFO [ChatPersistenceManager] Updated existing chat file: copilot/copilot-conversations/测试@20260901_190318.md
2026-09-01T11:35:08.744Z ERROR [ChatPersistenceManager] Error generating AI topic: Connection error.\nmore message: Failed to fetch\nError: Connection error.\n    at en.makeRequest (plugin:copilot:273:4456)\n    at async eval (plugin:copilot:280:61047)\n    at async Q2 (plugin:copilot:203:24170)\n    at async i (plugin:copilot:202:8726)
### Prompt — 2026-09-01T11:34:39.511Z

**Actual Messages Sent to LLM:**

```json
[
  {
    "role": "system",
    "content": "You are Obsidian Copilot, a helpful assistant that integrates AI to Obsidian note-taking.\n  1. Never mention that you do not have access to something. Always rely on the user provided context.\n  2. Always answer to the best of your knowledge. If you are unsure about something, say so and ask the user to provide more context.\n  3. If the user mentions \"note\", it most likely means an Obsidian note in the vault, not the generic meaning of a note.\n  4. If the user mentions \"@vault\", it means the user wants you to search the Obsidian vault for information relevant to the query. The search results will be provided to you in the context along with the user query, read it carefully and answer the question based on the information provided. If there's no relevant information in the vault, just say so.\n  5. If the user mentions any other tool with the @ symbol, check the context for their results. If nothing is found, just ignore the @ symbol in the query.\n  6. Always use $'s instead of \\[ etc. for LaTeX equations.\n  7. When showing note titles, use [[title]] format and do not wrap them in ` `.\n  8. When showing **Obsidian internal** image links, use ![[link]] format and do not wrap them in ` `.\n  9. When showing **web** image links, use ![link](url) format and do not wrap them in ` `.\n  10. When generating a table, format as github markdown tables, however, for table headings, immediately add ' |' after the table heading.\n  11. Always respond in the language of the user's query.\n  12. Do NOT mention the additional context provided such as getCurrentTime and getTimeRangeMs if it's irrelevant to the user message.\n  13. If the user mentions \"tags\", it most likely means tags in Obsidian note properties.\n  14. YouTube URLs: If the user provides YouTube URLs in their message, transcriptions will be automatically fetched and provided to you. You don't need to do anything special - just use the transcription content if available.\n  15. For markdown lists, always use '- ' (hyphen followed by exactly one space) for bullet points, with no leading spaces before the hyphen. Never use '*' (asterisk) for bullets.\n\n## Context Library\n\nThe following notes are available for reference:\n\n<active_note>\n<title>ToDo-已经规划好的任务</title>\n<path>非笔记内容/任务计划/ToDo-已经规划好的任务.md</path>\n<ctime>2026-09-01T08:52:45.081Z</ctime>\n<mtime>2026-09-01T08:52:34.173Z</mtime>\n<content>\n#时间管理 \n\n**目前我已经放假*** \n⏳代表 scheduled day；📅代表 deadline；1 🍅 = 40 分钟 ; 🔁代表recurring 例如- [ ] #task a 🔁 every day 📅 2026-07-24 \n\n**周六周天不要布置其他任务, 周一下午午休到两点之后可以布置任务, 除了上课前两小时之外, 不需要备课**\n\n# 2026-07-27 假期任务规划\n\n## 1. 数学学习\n\n## 2. 家教授课与备课\n\n\n\n\n# 2026-07-31 假期任务规划\n\n## 1. 数学学习\n\n\n## 2. 生活与设备\n\n\n\n\n\n- [ ] #task 做完GTM259 §2.1选择的习题 [🍅:: 2/4] 🔼 ⏳ 2026-09-01 📅 2026-09-01 ^73e1e9cd\n\n- [ ] #task 回看GTM259 Ch.1 §1.1–1.2 [🍅:: 0/1] 🔼 ⏳ 2026-09-01 ^b24fc7b0\n\n\n# 2026-08-09 假期任务规划\n\n## 1. 健康训练\n\n- [ ] #task 第1–4周膝盖恢复期：完成周一低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Monday ⏳ 2026-08-17 ^h26080901\n- [ ] #task 第1–4周膝盖恢复期：完成周二飞机杯行为训练、30秒记录和呼吸/盆底 ⏳ 2026-08-18 [🍅:: 0/1] 🔁 every week on Tuesday ^h26080902\n- [ ] #task 第1–4周膝盖恢复期：完成周三低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Wednesday ⏳ 2026-08-12 ^h26080903\n- [ ] #task 第1–4周膝盖恢复期：完成周四飞机杯行为训练、30秒记录和呼吸/盆底 [🍅:: 0/1] 🔁 every week on Thursday ⏳ 2026-08-13 ^h26080904\n- [ ] #task 第1–4周膝盖恢复期：完成周五低膝负荷有氧20分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Friday ⏳ 2026-08-14 ^h26080905\n- [ ] #task 第1–4周膝盖恢复期：完成周六飞机杯训练或双周标准化测试，并做呼吸/盆底 [🍅:: 0/1] 🔁 every week on Saturday ⏳ 2026-08-15 ^h26080906\n- [ ] #task 第1–4周膝盖恢复期：完成周日低膝负荷有氧20分钟、呼吸/盆底和本周记录快看 ⏳ 2026-08-16 [🍅:: 0/1] 🔁 every week on Sunday ^h26080907\n- [ ] #task 每4周完成一次健康训练阶段评估（硬度、控制、焦虑、时间、性兴趣） [🍅:: 0/1] 🔁 every 4 weeks on Sunday ⏳ 2026-08-30 ^h26080908\n\n## 2. 返校后健康维持\n\n- [ ] #task 第5–12周返校阶段：周一力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Monday ⏳ 2026-09-07 ^h26080909\n- [ ] #task 第5–12周返校阶段：周二完成飞机杯训练15分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Tuesday ⏳ 2026-09-08 ^h26080910\n- [ ] #task 第5–12周返校阶段：周三力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Wednesday ⏳ 2026-09-09 ^h26080911\n- [ ] #task 第5–12周返校阶段：周四完成飞机杯训练15分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Thursday ⏳ 2026-09-10 ^h26080912\n- [ ] #task 第5–12周返校阶段：周五力量后完成有氧30分钟和呼吸/盆底5分钟 [🍅:: 0/1] 🔁 every week on Friday ⏳ 2026-09-11 ^h26080913\n- [ ] #task 第5–12周返校阶段：周六完成飞机杯训练或双周标准化测试，并做呼吸/盆底 [🍅:: 0/1] 🔁 every week on Saturday ⏳ 2026-09-12 ^h26080914\n- [ ] #task 第5–12周返校阶段：周日完成有氧30分钟、呼吸/盆底和本周记录快看 [🍅:: 0/1] 🔁 every week on Sunday ⏳ 2026-09-06 ^h26080915\n\n> 计划备注：本批次来自 [[非笔记内容/任务计划/健康计划.md]]。第1–4周按膝盖恢复期执行，低膝负荷有氧优先；第5–12周在膝盖基本恢复且可恢复运动后执行。单日专项均按 1 🍅 记录；5分钟呼吸/盆底若单独执行则不估计番茄钟。双周标准化测试替代当周一次飞机杯训练，不额外增加一次训练。\n\n# 2026-08-31 目标模式启动任务\n\n- [ ] #task 学习GTM259 §2.2 Recurrence并重建Poincaré复现证明 [🍅:: 0/5] 🔼 ⏳ 2026-09-03 📅 2026-09-03 ^e260902a\n- [ ] #task 复习抽象代数群论基础与商群同构 [🍅:: 0/5] 🔼 ⏳ 2026-09-02 📅 2026-09-02 ^p260903a\n- [ ] #task 完成GTM259 §2.2习题与证明复述 [🍅:: 0/5] 🔼 ⏳ 2026-09-05 📅 2026-09-05 ^e260903a\n- [ ] #task 复习抽象代数群作用与Sylow定理 [🍅:: 0/3] 🔼 ⏳ 2026-09-04 📅 2026-09-04 ^p260904a\n- [ ] #task 完成抽象代数Sylow定理选题基线 [🍅:: 0/4] 🔼 ⏳ 2026-09-06 📅 2026-09-06 ^a260906a\n\n> 计划备注：本批次来自用户 2026-08-31 对目标模式的直接更正，执行细则见 [[07-概率论教材更正与近期学习启动]]。这些是 GTM259 与抽象代数先行任务；概率论等待真实课堂笔记后再接管，不代表老师已讲到相应内容；真实概率论课堂或作业出现时优先接管同一容量。周末只保留本批次已列出的目标模式学习块，不再叠加其他事项。\n\n\n</content>\n</active_note>"
  },
  {
    "role": "user",
    "content": "测试"
  },
  {
    "role": "assistant",
    "content": "\n<errorChunk>Connection error.\nmore message: Failed to fetch</errorChunk>"
  },
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "请只回复：COPILOT_OK"
      }
    ]
  }
]
```

**Layered Context Metadata:**

```
msg:msg-1788262479421-60x8s6urt | conv:N/A | v1

━━━ SYSTEM MESSAGE ━━━

🔒 L1_SYSTEM (18632c19) [CACHEABLE]
You are Obsidian Copilot, a helpful assistant that integrates AI to Obsidian note-taking.
  1. Never mention that you do not have access to something. Always rely on the user provided context.
  2. Always answer to the best of your knowledge. If you are unsure about something, say so and ask the use...[truncated]

🔒 L2_PREVIOUS (a0379917) [CACHEABLE]
<active_note>
<title>ToDo-已经规划好的任务</title>
<path>非笔记内容/任务计划/ToDo-已经规划好的任务.md</path>
<ctime>2026-09-01T08:52:45.081Z</ctime>
<mtime>2026-09-01T08:52:34.173Z</mtime>
<content>
#时间管理 

**目前我已经放假*** 
⏳代表 scheduled day；📅代表 deadline；1 🍅 = 40 分钟 ; 🔁代表recurring 例如- [ ] #task a 🔁 every day 📅 2026-07-24 ...[truncated]

━━━ CHAT HISTORY (L4) ━━━

2 message(s)

━━━ USER MESSAGE ━━━

⚡ L5_USER (defadd77)
请只回复：COPILOT_OK

```


## Settings
```json
{
  "userId": "87d81a0e-c2ce-4957-b38c-713f60f3a13f",
  "isPlusUser": false,
  "amazonBedrockRegion": "",
  "githubCopilotTokenExpiresAt": 0,
  "defaultChainType": "llm_chain",
  "defaultModelKey": "gpt-5.6-sol|3rd party (openai-format)",
  "embeddingModelKey": "Qwen/Qwen3-Embedding-0.6B|siliconflow",
  "temperature": 0.1,
  "maxTokens": 6000,
  "contextTurns": 15,
  "userSystemPrompt": "",
  "openAIProxyBaseUrl": "",
  "openAIEmbeddingProxyBaseUrl": "",
  "stream": true,
  "defaultSaveFolder": "copilot/copilot-conversations",
  "defaultConversationTag": "copilot-conversation",
  "autosaveChat": true,
  "generateAIChatTitleOnSave": true,
  "autoAddActiveContentToContext": true,
  "defaultOpenArea": "view",
  "defaultSendShortcut": "enter",
  "customPromptsFolder": "copilot/copilot-custom-prompts",
  "indexVaultToVectorStore": "ON MODE SWITCH",
  "qaExclusions": "copilot,%E9%99%84%E4%BB%B6,Excalidraw,markdown%20output",
  "qaInclusions": "",
  "chatNoteContextPath": "",
  "chatNoteContextTags": [],
  "enableIndexSync": true,
  "debug": false,
  "maxSourceChunks": 25,
  "enableInlineCitations": true,
  "activeModels": [
    {
      "name": "copilot-plus-flash",
      "provider": "copilot-plus",
      "enabled": true,
      "isBuiltIn": true,
      "core": true,
      "plusExclusive": true,
      "projectEnabled": false,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "google/gemini-2.5-flash",
      "provider": "openrouterai",
      "enabled": true,
      "isBuiltIn": true,
      "core": true,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "gpt-5.5",
      "provider": "openai",
      "enabled": false,
      "isBuiltIn": true,
      "core": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "gpt-5.4-mini",
      "provider": "openai",
      "enabled": false,
      "isBuiltIn": true,
      "core": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "google/gemini-3.5-flash",
      "provider": "openrouterai",
      "enabled": false,
      "isBuiltIn": true,
      "projectEnabled": true,
      "capabilities": [
        "reasoning",
        "vision"
      ]
    },
    {
      "name": "claude-sonnet-4-6",
      "provider": "anthropic",
      "enabled": false,
      "isBuiltIn": true,
      "capabilities": [
        "reasoning",
        "vision"
      ]
    },
    {
      "name": "gemini-3.5-flash",
      "provider": "google",
      "enabled": false,
      "isBuiltIn": true,
      "projectEnabled": true,
      "capabilities": [
        "reasoning",
        "vision"
      ]
    },
    {
      "name": "gemini-3.1-flash-lite",
      "provider": "google",
      "enabled": false,
      "isBuiltIn": true,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "gemini-2.5-flash",
      "provider": "google",
      "enabled": false,
      "isBuiltIn": true,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "google/gemini-3.1-pro-preview",
      "provider": "openrouterai",
      "enabled": false,
      "isBuiltIn": true,
      "capabilities": [
        "reasoning",
        "vision"
      ]
    },
    {
      "name": "google/gemini-2.5-pro",
      "provider": "openrouterai",
      "enabled": false,
      "isBuiltIn": true,
      "core": false,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "openai/gpt-5.5",
      "provider": "openrouterai",
      "enabled": false,
      "isBuiltIn": true,
      "core": false,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "openai/gpt-5.4-mini",
      "provider": "openrouterai",
      "enabled": false,
      "isBuiltIn": true,
      "core": false,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "grok-4.3",
      "provider": "xai",
      "enabled": false,
      "isBuiltIn": true,
      "core": false,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "x-ai/grok-4.3",
      "provider": "openrouterai",
      "enabled": false,
      "isBuiltIn": true,
      "core": false,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "gpt-4.1",
      "provider": "openai",
      "enabled": false,
      "isBuiltIn": true,
      "core": false,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "gpt-4.1-mini",
      "provider": "openai",
      "enabled": false,
      "isBuiltIn": true,
      "core": false,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "claude-opus-4-7",
      "provider": "anthropic",
      "enabled": false,
      "isBuiltIn": true,
      "capabilities": [
        "reasoning",
        "vision"
      ]
    },
    {
      "name": "claude-haiku-4-5",
      "provider": "anthropic",
      "enabled": false,
      "isBuiltIn": true,
      "capabilities": [
        "reasoning",
        "vision"
      ]
    },
    {
      "name": "gemini-3.1-pro-preview",
      "provider": "google",
      "enabled": false,
      "isBuiltIn": true,
      "capabilities": [
        "reasoning",
        "vision"
      ]
    },
    {
      "name": "gemini-2.5-pro",
      "provider": "google",
      "enabled": false,
      "isBuiltIn": true,
      "projectEnabled": true,
      "capabilities": [
        "vision"
      ]
    },
    {
      "name": "deepseek-chat",
      "provider": "deepseek",
      "enabled": false,
      "isBuiltIn": true
    },
    {
      "name": "deepseek-reasoner",
      "provider": "deepseek",
      "enabled": false,
      "isBuiltIn": true,
      "capabilities": [
        "reasoning"
      ]
    },
    {
      "name": "deepseek-ai/DeepSeek-V3",
      "provider": "siliconflow",
      "enabled": false,
      "isBuiltIn": false,
      "baseUrl": "https://api.siliconflow.com/v1"
    },
    {
      "name": "deepseek-ai/DeepSeek-R1",
      "provider": "siliconflow",
      "enabled": false,
      "isBuiltIn": false,
      "baseUrl": "https://api.siliconflow.com/v1",
      "capabilities": [
        "reasoning"
      ]
    },
    {
      "name": "deepseek-v4-pro",
      "provider": "deepseek",
      "enabled": true,
      "isBuiltIn": false,
      "baseUrl": "https://api.deepseek.com",
      "isEmbeddingModel": false,
      "capabilities": [
        "reasoning"
      ],
      "stream": true,
      "displayName": "deepseek-v4 pro"
    },
    {
      "name": "gpt-5.6-sol",
      "provider": "3rd party (openai-format)",
      "enabled": true,
      "isBuiltIn": false,
      "baseUrl": "https://sub2api.52ai.pro/v1",
      "isEmbeddingModel": false,
      "capabilities": [
        "reasoning"
      ],
      "stream": true
    }
  ],
  "activeEmbeddingModels": [
    {
      "name": "copilot-plus-small",
      "provider": "copilot-plus",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true,
      "plusExclusive": true
    },
    {
      "name": "copilot-plus-large",
      "provider": "copilot-plus-jina",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true,
      "plusExclusive": true,
      "believerExclusive": true,
      "dimensions": 1024
    },
    {
      "name": "copilot-plus-multilingual",
      "provider": "copilot-plus-jina",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true,
      "plusExclusive": true,
      "dimensions": 512
    },
    {
      "name": "openai/text-embedding-3-small",
      "provider": "openrouterai",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true
    },
    {
      "name": "text-embedding-3-small",
      "provider": "openai",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true
    },
    {
      "name": "gemini-embedding-001",
      "provider": "google",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true,
      "enableCors": true
    },
    {
      "name": "gemini-embedding-2-preview",
      "provider": "google",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true,
      "enableCors": true
    },
    {
      "name": "Qwen/Qwen3-Embedding-0.6B",
      "provider": "siliconflow",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "core": true,
      "baseUrl": "https://api.siliconflow.com/v1",
      "enableCors": true
    },
    {
      "name": "text-embedding-3-large",
      "provider": "openai",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true
    },
    {
      "name": "embed-multilingual-light-v3.0",
      "provider": "cohereai",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true
    },
    {
      "name": "text-embedding-004",
      "provider": "google",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true,
      "enableCors": true
    },
    {
      "name": "azure-openai",
      "provider": "azure openai",
      "enabled": true,
      "isBuiltIn": true,
      "isEmbeddingModel": true
    },
    {
      "name": "text-embedding-bge-large-zh-v1.5",
      "provider": "lm-studio",
      "enabled": true,
      "isBuiltIn": false,
      "baseUrl": "",
      "isEmbeddingModel": true,
      "capabilities": [],
      "displayName": "",
      "enableCors": true
    }
  ],
  "embeddingRequestsPerMin": 60,
  "embeddingBatchSize": 16,
  "disableIndexOnMobile": true,
  "showSuggestedPrompts": false,
  "showRelevantNotes": true,
  "numPartitions": 1,
  "lexicalSearchRamLimit": 100,
  "promptUsageTimestamps": {},
  "promptSortStrategy": "timestamp",
  "chatHistorySortStrategy": "recent",
  "projectListSortStrategy": "recent",
  "projectsFolder": "copilot/projects",
  "defaultConversationNoteName": "{$topic}@{$date}_{$time}",
  "inlineEditCommands": [],
  "projectList": [],
  "lastDismissedVersion": "3.3.3",
  "passMarkdownImages": true,
  "enableAutonomousAgent": false,
  "enableCustomPromptTemplating": true,
  "enableSemanticSearchV3": true,
  "enableSelfHostMode": false,
  "enableMiyo": false,
  "miyoSearchAll": false,
  "selfHostModeValidatedAt": null,
  "selfHostValidationCount": 0,
  "selfHostUrl": "",
  "miyoServerUrl": "",
  "selfHostSearchProvider": "firecrawl",
  "enableLexicalBoosts": true,
  "suggestedDefaultCommands": true,
  "autonomousAgentMaxIterations": 4,
  "autonomousAgentEnabledToolIds": [
    "localSearch",
    "webSearch",
    "pomodoro",
    "youtubeTranscription",
    "writeFile",
    "editFile"
  ],
  "reasoningEffort": "low",
  "verbosity": "medium",
  "memoryFolderName": "copilot/memory",
  "enableRecentConversations": false,
  "maxRecentConversations": 30,
  "enableSavedMemory": false,
  "quickCommandIncludeNoteContext": true,
  "autoIncludeTextSelection": false,
  "autoAddSelectionToContext": false,
  "autoAcceptEdits": true,
  "diffViewMode": "split",
  "userSystemPromptsFolder": "copilot/system-prompts",
  "defaultSystemPromptTitle": "",
  "autoCompactThreshold": 128000,
  "convertedDocOutputFolder": "",
  "includeActiveNoteAsContext": true,
  "enableAutocomplete": false,
  "autocompleteAcceptKey": "Tab",
  "allowAdditionalContext": true,
  "enableWordCompletion": false,
  "_keychainVaultId": "b6e27d05"
}
```
