import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AgentStep, SSEEvent, FullResult } from '../types'
import { createDevelopmentStream, approveSpec, generatePrd } from '../api/development'

export const useDevelopmentStore = defineStore('development', () => {
  const requirement = ref('')
  const isRunning = ref(false)
  const currentStep = ref<AgentStep>('idle')
  const architecture = ref('')
  const spec = ref('')
  const code = ref('')
  const testReport = ref('')
  const deploymentPlan = ref('')
  const errorMessage = ref('')
  // 审批流程新增
  const awaitingApproval = ref(false)
  const sessionId = ref('')
  const pendingSpec = ref('')
  const skillContext = ref('')
  // 仅生成 PRD 模式
  const prdOnlyMode = ref(false)
  const prdLoading = ref(false)
  let abortFn: (() => void) | null = null

  const progress = computed(() => {
    const map: Record<AgentStep, number> = {
      idle: 0,
      pm: 20,
      await_approval: 20,
      arch: 40,
      dev: 60,
      test: 80,
      devops: 90,
      done: 100,
      error: 0,
    }
    return map[currentStep.value]
  })

  function startDevelopment(req: string) {
    if (isRunning.value) return
    requirement.value = req
    isRunning.value = true
    currentStep.value = 'idle'
    architecture.value = ''
    spec.value = ''
    code.value = ''
    testReport.value = ''
    deploymentPlan.value = ''
    errorMessage.value = ''

    abortFn = createDevelopmentStream(
      req,
      (event: SSEEvent) => {
        switch (event.type) {
          case 'status':
            if (event.data.includes('产品经理')) currentStep.value = 'pm'
            else if (event.data.includes('架构师')) currentStep.value = 'arch'
            else if (event.data.includes('开发工程师')) currentStep.value = 'dev'
            else if (event.data.includes('测试工程师')) currentStep.value = 'test'
            else if (event.data.includes('部署工程师')) currentStep.value = 'devops'
            break
          case 'product_manager':
            spec.value = event.data as string
            currentStep.value = 'pm'
            break
          case 'await_approval':
            pendingSpec.value = event.data as string
            if ((event as any).skill_context) {
              skillContext.value = (event as any).skill_context as string
            }
            awaitingApproval.value = true
            isRunning.value = false
            currentStep.value = 'await_approval'
            break
          case 'architect':
            architecture.value = event.data as string
            currentStep.value = 'arch'
            break
          case 'developer':
            code.value = event.data as string
            currentStep.value = 'dev'
            break
          case 'tester':
            testReport.value = event.data as string
            currentStep.value = 'test'
            break
          case 'devops':
            deploymentPlan.value = event.data as string
            currentStep.value = 'devops'
            break
          case 'complete': {
            const result = event.data as FullResult
            architecture.value = result.architecture
            spec.value = result.spec
            code.value = result.code
            testReport.value = result.test_report
            deploymentPlan.value = result.deployment_plan
            currentStep.value = 'done'
            isRunning.value = false
            break
          }
          case 'error':
            errorMessage.value = event.data as string
            currentStep.value = 'error'
            isRunning.value = false
            break
        }
      },
      (err: Error) => {
        errorMessage.value = err.message
        currentStep.value = 'error'
        isRunning.value = false
      }
    )
  }

  function cancel() {
    abortFn?.()
    isRunning.value = false
    currentStep.value = 'idle'
  }

  function reset() {
    cancel()
    requirement.value = ''
    architecture.value = ''
    spec.value = ''
    code.value = ''
    testReport.value = ''
    deploymentPlan.value = ''
    errorMessage.value = ''
    awaitingApproval.value = false
    sessionId.value = ''
    pendingSpec.value = ''
    prdOnlyMode.value = false
    prdLoading.value = false
  }

  async function generatePrdOnly(req: string) {
    if (isRunning.value) return
    requirement.value = req
    isRunning.value = true
    prdOnlyMode.value = true
    prdLoading.value = true
    errorMessage.value = ''

    try {
      const result = await generatePrd(req)
      spec.value = result.spec
      code.value = ''
      testReport.value = ''
      deploymentPlan.value = ''
      architecture.value = ''
    } catch (err: any) {
      errorMessage.value = err.message || 'PRD 生成失败'
    } finally {
      isRunning.value = false
      prdLoading.value = false
    }
  }

  function approveSpecFlow(modifiedSpec: string) {
    if (!sessionId.value) return
    abortFn = approveSpec(
      sessionId.value,
      modifiedSpec,
      skillContext.value,
      (event: SSEEvent) => {
        switch (event.type) {
          case 'status':
            if (event.data.includes('架构师')) currentStep.value = 'arch'
            else if (event.data.includes('开发工程师')) currentStep.value = 'dev'
            else if (event.data.includes('测试工程师')) currentStep.value = 'test'
            else if (event.data.includes('部署工程师')) currentStep.value = 'devops'
            break
          case 'architect':
            architecture.value = event.data as string
            currentStep.value = 'arch'
            break
          case 'developer':
            code.value = event.data as string
            currentStep.value = 'dev'
            break
          case 'tester':
            testReport.value = event.data as string
            currentStep.value = 'test'
            break
          case 'devops':
            deploymentPlan.value = event.data as string
            currentStep.value = 'devops'
            break
          case 'complete': {
            const result = event.data as FullResult
            architecture.value = result.architecture
            spec.value = result.spec
            code.value = result.code
            testReport.value = result.test_report
            deploymentPlan.value = result.deployment_plan
            currentStep.value = 'done'
            isRunning.value = false
            awaitingApproval.value = false
            break
          }
          case 'error':
            errorMessage.value = event.data as string
            currentStep.value = 'error'
            isRunning.value = false
            awaitingApproval.value = false
            break
        }
      },
      (err: Error) => {
        errorMessage.value = err.message
        currentStep.value = 'error'
        isRunning.value = false
        awaitingApproval.value = false
      }
    )
  }

  return {
    requirement,
    isRunning,
    currentStep,
    architecture,
    spec,
    code,
    testReport,
    deploymentPlan,
    errorMessage,
    awaitingApproval,
    sessionId,
    pendingSpec,
    prdOnlyMode,
    prdLoading,
    progress,
    startDevelopment,
    generatePrdOnly,
    approveSpecFlow,
    cancel,
    reset,
  }
})
