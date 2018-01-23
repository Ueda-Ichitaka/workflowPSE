import { Artefact } from 'app/models/Artefact';

export enum TaskState {
    NONE,
    READY,
    WAITING,
    RUNNING,
    FINISHED,
    FAILED,
    DEPRECATED
}

export interface Task {
    id: number;
    x: number;
    y: number;
    state: TaskState;
    process_id: number;
    input_artefacts: Artefact<'input'>[];
    ouput_artefacts: Artefact<'output'>[];
    created_at: number;
    updated_at: number;
}
