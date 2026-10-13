"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {evaluateTask} = require("./app.js");
const normal={task_id:"T1",target_identifier:"S1",primary_metric:"25",secondary_metric:"12",status_descriptor:"NOMINAL",is_critical_flag:false};
test("rule boundaries are nominal",()=>{const r=evaluateTask(normal);assert.equal(r.overall_urgency,"ROUTINE");assert.equal(r.total_alerts,0)});
test("secondary threshold and manual priority",()=>{assert.equal(evaluateTask({...normal,secondary_metric:"12.1"}).overall_urgency,"ELEVATED_RISK");assert.equal(evaluateTask({...normal,is_critical_flag:true}).overall_urgency,"CRITICAL_STAT_PANIC")});
test("primary threshold and anomaly keywords",()=>{assert.equal(evaluateTask({...normal,primary_metric:"25.01",status_descriptor:"anomaly"}).total_alerts,2)});
test("bad inputs rejected",()=>{for(const value of ["","Infinity","NaN"])assert.throws(()=>evaluateTask({...normal,primary_metric:value}));assert.throws(()=>evaluateTask({...normal,task_id:" "}));assert.throws(()=>evaluateTask({...normal,status_descriptor:" "}))});
