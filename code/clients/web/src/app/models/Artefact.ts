export interface Artefact<T> {
    parameter_id: number;
    task_id: number;
    workflow_id: number;
    role: T;
    format: string;
    data: string;
    created_at: number;
    updated_at: number;
}
