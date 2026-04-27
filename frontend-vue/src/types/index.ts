export type AgentStep = 'idle' | 'pm' | 'dev' | 'test' | 'devops' | 'done' | 'error'

export interface SSEEvent {
  type: 'status' | 'product_manager' | 'developer' | 'tester' | 'devops' | 'complete' | 'error'
  data: string | FullResult
  done: boolean
}

export interface FullResult {
  requirement: string
  spec: string
  code: string
  test_report: string
  deployment_plan: string
  history: string[]
}

export interface DevelopmentState {
  requirement: string
  isRunning: boolean
  currentStep: AgentStep
  spec: string
  code: string
  testReport: string
  deploymentPlan: string
  errorMessage: string
}
