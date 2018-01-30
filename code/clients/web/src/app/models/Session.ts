import { Workflow } from './Workflow'

export interface Session {
	id: number
	isAuthenticated: boolean
	workflow: Workflow
	language: String
	isAdmin: boolean
}
