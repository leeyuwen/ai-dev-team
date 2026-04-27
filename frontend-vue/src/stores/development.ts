import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AgentStep, SSEEvent, FullResult } from '../types'
import { createDevelopmentStream } from '../api/development'

export const useDevelopmentStore = defineStore('development', () => {
  const requirement = ref('')
  const isRunning = ref(false)
  const currentStep = ref<AgentStep>('idle')
  const spec = ref('')
  const code = ref('')
  const testReport = ref('')
  const deploymentPlan = ref('')
  const errorMessage = ref('')

  let abortFn: (() => void) | null = null

  const progress = computed(() => {
    const map: Record<AgentStep, number> = {
      idle: 0,
      pm: 25,
      dev: 50,
      test: 75,
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
            // derive step from message
            if (event.data.includes('产品经理')) currentStep.value = 'pm'
            else if (event.data.includes('开发工程师')) currentStep.value = 'dev'
            else if (event.data.includes('测试工程师')) currentStep.value = 'test'
            else if (event.data.includes('部署工程师')) currentStep.value = 'devops'
            break
          case 'product_manager':
            spec.value = event.data as string
            currentStep.value = 'pm'
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
    spec.value = ''
    code.value = ''
    testReport.value = ''
    deploymentPlan.value = ''
    errorMessage.value = ''
  }

  return {
    requirement,
    isRunning,
    currentStep,
    spec,
    code,
    testReport,
    deploymentPlan,
    errorMessage,
    progress,
    startDevelopment,
    cancel,
    reset,
  }
})
