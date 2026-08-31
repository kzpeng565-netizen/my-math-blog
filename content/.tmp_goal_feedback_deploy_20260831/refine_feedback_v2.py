from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP = ROOT / "garden" / "static" / "app.js"
BACKEND = ROOT / "advisor" / "src" / "goal_agent.py"


def replace_js_function(text: str, name: str, replacement: str) -> str:
    pattern = rf"function {re.escape(name)}\([^\n]*?(?=\nfunction |\nasync function |\nlet goalQuickChoices)"
    updated, count = re.subn(pattern, replacement.rstrip(), text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"could not replace JS function {name}: {count}")
    return updated


app = APP.read_text(encoding="utf-8")
app = replace_js_function(
    app,
    "openGoalFeedback",
    r'''function goalTrackForKind(kind){return({course:'track-courses',grade:'track-courses',mock:'track-amss-exam',reading:'track-ergodic',talk:'track-ergodic',oral:'track-algebra'}[kind]||'track-courses')}
function openGoalFeedback(itemId='',kind='',course=''){goalView('evidence');const data=state.goal.data||{},items=data.current_week?.items||[],item=items.find(value=>value.id===itemId);const select=$('#goalFeedbackItem');if(select)select.value=itemId||'';const type=$('#goalFeedbackType'),selectedKind=kind||goalFeedbackKindForItem(item);if(type)type.value=selectedKind;$('#goalFeedbackTrack').value=item?.track_id||goalTrackForKind(selectedKind);goalQuickCourse=course||item?.course_id&&((data.course_profiles||[]).find(profile=>profile.id===item.course_id)?.name)||'';renderGoalQuickForm(data);requestAnimationFrame(()=>$('#goal-view-evidence')?.scrollIntoView({behavior:'smooth',block:'start'}))}''',
)
app = replace_js_function(
    app,
    "goalQuickCourses",
    r'''function goalQuickCourses(data){return`<label>课程<select id="goalFeedbackCourse"><option value="">请选择</option>${(data.course_profiles||[]).map(profile=>`<option value="${escapeHtml(profile.name)}" ${profile.name===goalQuickCourse?'selected':''}>${escapeHtml(profile.name)}</option>`).join('')}</select></label>`}
function renderGoalGradeComponents(data){const root=$('#goalGradeComponentPicker');if(!root)return;const course=$('#goalFeedbackCourse')?.value||goalQuickCourse,profile=(data.course_profiles||[]).find(item=>item.name===course),labels={midterm:'期中',final:'期末',homework:'作业',thinking_problems:'思考题',coursework:'平时'};const weights=Object.entries(profile?.assessment_weights||{});root.innerHTML=weights.length?`<label>考核项目<select id="goalQuickComponent"><option value="">请选择</option>${weights.map(([key,value])=>`<option value="${escapeHtml(key)}" data-weight="${Number(value)}">${escapeHtml(labels[key]||key)} · ${Math.round(Number(value)*100)}%</option>`).join('')}</select></label>`:'<label>考核项目<input id="goalQuickComponent" maxlength="100" placeholder="考核比例尚未确认"></label><p class="setting-help">没有确认比例时只保存原始成绩，不计算总评情景。</p>'}''',
)
app = replace_js_function(
    app,
    "renderGoalQuickForm",
    r'''function renderGoalQuickForm(data){goalQuickChoices={};const kind=$('#goalFeedbackType').value,root=$('#goalQuickFields');let html='';if(kind==='course'){html=goalQuickCourses(data)+`<section id="goalCourseProgressFields" class="goal-course-progress-fields"><div><h3>确认实际讲到的小节</h3><p class="setting-help">勾选小节；共同掌握度可一次应用，再按小节改动。</p></div><div id="goalCourseUnitPicker" class="goal-course-unit-picker"></div>${goalQuickGroup('所选小节共同掌握度','common_mastery',Object.entries(goalMasteryLabels))}${goalQuickGroup('这次掌握度依据','basis',goalQuickOptions.basis)}</section>`}else if(kind==='exercise'){html=`<div class="goal-form-grid">${goalQuickNumber('goalQuickAttempted','尝试题数','例如 10')}${goalQuickNumber('goalQuickCorrect','最终做对','未核对可留空')}</div>${goalQuickGroup('完成情况','result',goalQuickOptions.result)}${goalQuickGroup('解题时用了多少帮助？','assistance',goalQuickOptions.assistance)}${goalQuickGroup('正确数怎么核对？','verification',goalQuickOptions.verification)}<label>题组 / 来源<input id="goalQuickSource" maxlength="160" placeholder="如：作业1第1–10题；代数书面任务必填"></label>`}else if(kind==='proof'){html=`${goalQuickGroup('这次能做到','proof_result',[['independent','独立完成'],['hinted','提示后完成'],['partial','只完成一部分'],['blocked','尚未完成']])}${goalQuickGroup('本次属于','attempt_timing',[['first','首次尝试'],['immediate','即时重做'],['delayed','隔日复测'],['unknown','不确定']])}${goalQuickGroup('怎么核对？','verification',goalQuickOptions.verification)}<label>命题 / 证明对象<input id="goalQuickObject" maxlength="200" placeholder="自动关联不准确时补充"></label>`}else if(kind==='grade'){html=`${goalQuickCourses(data)}<div id="goalGradeComponentPicker"></div><div class="goal-form-grid">${goalQuickNumber('goalQuickScore','得分','真实值')}${goalQuickNumber('goalQuickMax','满分','例如 100')}</div>${goalQuickGroup('成绩来源','origin',[['official','老师 / 教务公布'],['self','对照标准自评'],['estimate','暂时估分']])}` }else if(kind==='mock'){html=`<label>真实题源 / 试卷 ID<input id="goalQuickSource" maxlength="160" placeholder="不同卷必须使用不同 ID"></label><div class="goal-form-grid">${goalQuickNumber('goalQuickScore','得分','未批改可留空',150)}${goalQuickNumber('goalQuickMax','满分','例如 150',150)}${goalQuickNumber('goalQuickElapsed','实际用时（分钟）','例如 120',1440)}</div>${goalQuickGroup('作答帮助','assistance',goalQuickOptions.assistance)}${goalQuickGroup('完成条件','condition',[['timed','完整限时'],['interrupted','有中断'],['untimed','非限时'],['unknown','未记录']])}${goalQuickGroup('题目熟悉度','novelty',[['new','首次见'],['repeat','做过 / 看过'],['mixed','部分见过'],['unknown','不确定']])}${goalQuickGroup('评分依据','verification',goalQuickOptions.verification)}` }else if(kind==='reading'){html=`${goalQuickGroup('本次进展','result',goalQuickOptions.result)}${goalQuickGroup('实际检验到哪一步？','quality',[['summary','能合书讲主线'],['proof','能重建关键证明'],['apply','能用于新例子'],['untested','还没有检验']])}${goalQuickNumber('goalQuickUnits','新增笔记页数（可选）','未统计可留空')}` }else if(kind==='talk'){html=`${goalQuickNumber('goalQuickUnits','实际讲解分钟','例如 20',1440)}${goalQuickGroup('讲解情况','talk_result',[['independent','连贯讲完'],['notes','频繁看笔记'],['blocked','没有讲完']])}${goalQuickGroup('追问表现','questions',[['independent','独立答出'],['hinted','提示后答出'],['failed','没有答出'],['untested','没有追问']])}${goalQuickGroup('评价者','rater',[['self','自己'],['peer','同学 / 老师'],['unknown','未评价']])}` }else if(kind==='oral'){html=`<p class="setting-help">四项 0–5；未测请选择“—”。</p><div class="goal-oral-grid">${['定义','例子','策略','追问'].map((label,index)=>`<label>${label}<select data-goal-oral="${index}"><option value="">—</option>${[0,1,2,3,4,5].map(value=>`<option value="${value}">${value}</option>`).join('')}</select></label>`).join('')}</div>${goalQuickGroup('评分者','rater',[['self','自己'],['peer','同学 / 老师'],['ai','AI 辅助']])}${goalQuickGroup('回答条件','assistance',[['none','独立回答'],['hint','有提示'],['solution','看了材料'],['unknown','未记录']])}` }else{html=`${goalQuickGroup('主要原因','blocked_reason',[['concept','概念不清'],['proof','证明卡住'],['material','缺资料'],['time','时间不足'],['other','其他']])}${goalQuickGroup('影响范围','impact',[['local','一个步骤'],['session','本次做不下去'],['recurring','多次反复'],['unknown','不确定']])}${goalQuickGroup('希望怎么处理','request',[['split','拆小任务'],['explain','补解释 / 前置'],['defer','重新建议日期']])}` }root.innerHTML=html;bindGoalQuickChoices(root);$('#goalFeedbackCourse')?.addEventListener('change',event=>{goalQuickCourse=event.target.value;if(kind==='course')renderGoalCourseUnitPicker(data);if(kind==='grade')renderGoalGradeComponents(data)});if(kind==='course')renderGoalCourseUnitPicker(data);if(kind==='grade')renderGoalGradeComponents(data);root.querySelectorAll('input').forEach(input=>input.addEventListener('input',renderGoalQuickAdaptive));renderGoalQuickAdaptive()}''',
)
app = replace_js_function(
    app,
    "submitGoalFeedback",
    r'''async function submitGoalFeedback(){const button=$('#goalFeedbackSubmit'),kind=$('#goalFeedbackType').value,itemId=$('#goalFeedbackItem').value||null,item=(state.goal.data?.current_week?.items||[]).find(value=>value.id===itemId),trackId=item?.track_id||$('#goalFeedbackTrack').value||goalTrackForKind(kind);let evidenceType='progress_update',score=null,maxScore=null,completedUnits=null,sourceId=null,blockedReason=null;const details={feedback_schema_version:2,feedback_kind:kind,performance:{},conditions:{},note:$('#goalFeedbackNote').value.trim()||null};if(kind==='course'){evidenceType='course_progress';const course=$('#goalFeedbackCourse').value,selected=$$('[data-goal-course-unit]:checked');if(!course||!selected.length||!goalQuickRequired(kind,['common_mastery','basis'])){if(!course||!selected.length)toast('请选择课程和实际讲到的小节。',true);return}details.course=course;details.taught_units=selected.map(box=>({unit_id:box.dataset.goalCourseUnit,mastery:Number($(`[data-goal-course-mastery="${CSS.escape(box.dataset.goalCourseUnit)}"]`).value)}));details.conditions.mastery_basis=goalQuickChoices.basis}else if(kind==='exercise'){if(!goalQuickRequired(kind,['result','assistance','verification']))return;const attempted=Number(goalQuickValue('goalQuickAttempted')),correctRaw=goalQuickValue('goalQuickCorrect'),correct=correctRaw===null?null:Number(correctRaw),independentRaw=goalQuickValue('goalQuickIndependent'),independent=independentRaw===null?null:Number(independentRaw);if(!Number.isInteger(attempted)||attempted<1||correct!==null&&(!Number.isInteger(correct)||correct<0||correct>attempted)||independent!==null&&(!Number.isInteger(independent)||independent<0||correct===null||independent>correct)){toast('请检查题数：尝试数至少 1，且独立做对 ≤ 最终做对 ≤ 尝试数。',true);return}evidenceType=item?.track_code==='algebra'?'algebra_written':'progress_update';details.performance={attempted,correct,independent_correct:goalQuickChoices.assistance==='none'?correct:independent,result:goalQuickChoices.result,error_type:goalQuickChoices.diagnostic||null};details.conditions={assistance:goalQuickChoices.assistance,verification:goalQuickChoices.verification};completedUnits=attempted;sourceId=goalQuickValue('goalQuickSource');if(evidenceType==='algebra_written'){if(!sourceId){toast('代数书面任务需要题组 / 来源 ID，避免重复题被计为连续达标。',true);return}score=correct;maxScore=attempted}}else if(kind==='proof'){if(!goalQuickRequired(kind,['proof_result','attempt_timing','verification']))return;details.performance={result:goalQuickChoices.proof_result,weak_step:goalQuickChoices.diagnostic||null,object:goalQuickValue('goalQuickObject')};details.conditions={attempt_timing:goalQuickChoices.attempt_timing,verification:goalQuickChoices.verification}}else if(kind==='grade'){if(!goalQuickRequired(kind,['origin']))return;evidenceType='course_component';score=Number(goalQuickValue('goalQuickScore'));maxScore=Number(goalQuickValue('goalQuickMax'));const course=$('#goalFeedbackCourse').value,component=$('#goalQuickComponent'),componentValue=component?.value||'',selectedOption=component?.selectedOptions?.[0],weight=selectedOption?.dataset?.weight===''||selectedOption?.dataset?.weight===undefined?null:Number(selectedOption.dataset.weight);if(!course||!componentValue){toast('请选择课程和考核项目。',true);return}if(!Number.isFinite(score)||!Number.isFinite(maxScore)||maxScore<=0||score<0||score>maxScore){toast('请填写有效得分和满分。',true);return}details.course=course;details.component=componentValue;if(Number.isFinite(weight))details.weight=weight;details.conditions={origin:goalQuickChoices.origin}}else if(kind==='mock'){if(!goalQuickRequired(kind,['assistance','condition','novelty','verification']))return;evidenceType='exam_mock';sourceId=goalQuickValue('goalQuickSource');if(!sourceId){toast('请选择或填写真实题源。',true);return}const scoreRaw=goalQuickValue('goalQuickScore'),maxRaw=goalQuickValue('goalQuickMax');score=scoreRaw===null?null:Number(scoreRaw);maxScore=maxRaw===null?null:Number(maxRaw);if((score===null)!==(maxScore===null)||score!==null&&(!Number.isFinite(score)||!Number.isFinite(maxScore)||maxScore<=0||score<0||score>maxScore)){toast('得分与满分请同时填写，并检查范围。',true);return}details.performance={elapsed_minutes:goalQuickValue('goalQuickElapsed')===null?null:Number(goalQuickValue('goalQuickElapsed'))};details.conditions={assistance:goalQuickChoices.assistance,completion:goalQuickChoices.condition,novelty:goalQuickChoices.novelty,verification:goalQuickChoices.verification}}else if(kind==='reading'){if(!goalQuickRequired(kind,['result','quality']))return;evidenceType='ergodic_note';completedUnits=goalQuickValue('goalQuickUnits')===null?null:Number(goalQuickValue('goalQuickUnits'));details.performance={result:goalQuickChoices.result,quality_check:goalQuickChoices.quality}}else if(kind==='talk'){if(!goalQuickRequired(kind,['talk_result','questions','rater']))return;evidenceType='ergodic_talk';completedUnits=Number(goalQuickValue('goalQuickUnits'));if(!Number.isFinite(completedUnits)||completedUnits<=0){toast('请填写有效讲解分钟。',true);return}details.performance={result:goalQuickChoices.talk_result,questions:goalQuickChoices.questions};details.conditions={rater:goalQuickChoices.rater}}else if(kind==='oral'){if(!goalQuickRequired(kind,['rater','assistance']))return;evidenceType='algebra_oral';const values=$$('[data-goal-oral]').map(select=>select.value===''?null:Number(select.value));if(values.every(value=>value===null)){toast('请至少填写一项口头测评。',true);return}details.oral_scores={definition:values[0],example:values[1],strategy:values[2],follow_up:values[3]};details.conditions={rater:goalQuickChoices.rater,assistance:goalQuickChoices.assistance}}else{if(!goalQuickRequired(kind,['blocked_reason','impact','request']))return;blockedReason=goalQuickChoices.blocked_reason;details.performance={impact:goalQuickChoices.impact};details.conditions={requested_response:goalQuickChoices.request}}const body={track_id:trackId,plan_item_id:itemId,evidence_type:evidenceType,deep_minutes:optionalNumber('#goalFeedbackMinutes'),status:$('#goalFeedbackStatus').value||null,score,max_score:maxScore,completed_units:completedUnits,source_id:sourceId,blocked_reason:blockedReason,details};button.disabled=true;try{const result=await goalWrite('/api/goal-agent/feedback',body,'feedback');const boundary=result.evidence_boundary||'证据已按原始条件保存；不足的部分保持待核验。';$('#goalEvidenceBoundary').textContent=boundary;toast('反馈已保存；AI 复盘将结合历史与资料，不会把单次自评当成完整结论');$('#goalFeedbackNote').value='';await loadGoalMode()}catch(error){toast(error.message,true)}finally{button.disabled=false}}''',
)
app = app.replace(
    "$('#goalFeedbackType').onchange=()=>renderGoalQuickForm(state.goal.data||{});",
    "$('#goalFeedbackType').onchange=event=>{if(!$('#goalFeedbackItem').value)$('#goalFeedbackTrack').value=goalTrackForKind(event.target.value);renderGoalQuickForm(state.goal.data||{})};",
)
APP.write_text(app, encoding="utf-8")


backend = BACKEND.read_text(encoding="utf-8")
backend = backend.replace(
    '''        for key in ("course", "component"):
            value = _clean_text(details.get(key), 120)
            if value:
                normalized[key] = value
''',
    '''        for key in ("course", "component"):
            value = _clean_text(details.get(key), 120)
            if value:
                normalized[key] = value
        weight = details.get("weight")
        if weight not in (None, ""):
            weight = float(weight)
            if not 0 < weight <= 1:
                raise ValueError("grade weight must be between 0 and 1")
            normalized["weight"] = weight
''',
)
backend = backend.replace(
    '''            if score_value not in (None, ""):
                score_value = float(score_value)
                if score_value < 0:
                    raise ValueError("score must be non-negative")
            if maximum_value not in (None, ""):
                maximum_value = float(maximum_value)
                if maximum_value <= 0:
                    raise ValueError("max_score must be positive")
''',
    '''            if score_value in (None, ""):
                score_value = None
            else:
                score_value = float(score_value)
                if score_value < 0:
                    raise ValueError("score must be non-negative")
            if maximum_value in (None, ""):
                maximum_value = None
            else:
                maximum_value = float(maximum_value)
                if maximum_value <= 0:
                    raise ValueError("max_score must be positive")
''',
)
backend = backend.replace(
    '''        context["public_search"] = {
            "status": public_search.get("status"),
            "result_count": len(public_search.get("results", [])),
        }
''',
    '''        context["public_search"] = {
            "status": public_search.get("status"),
            "result_count": len(public_search.get("results", [])),
        }
        query_parts: list[str] = []
        for event in context.get("recent_evidence", [])[-5:]:
            details = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            performance = details.get("performance") if isinstance(details.get("performance"), dict) else {}
            for value in (
                details.get("course"), details.get("component"), performance.get("object"),
                details.get("note"), event.get("source_id"),
            ):
                text = _clean_text(value, 160)
                if text:
                    query_parts.append(text)
        context["material_snippets"] = self.search_materials(" ".join(query_parts), limit=6) if query_parts else []
''',
    1,
)
BACKEND.write_text(backend, encoding="utf-8")
