import { Artefact } from 'app/models/Artefact';

/**
 * describes the current state of a task
 */
export enum TaskState {
    NONE,
    READY,
    WAITING,
    RUNNING,
    FINISHED,
    FAILED,
    DEPRECATED
}

/**
 * tasks describe the actual task elements which are
 * displayed in the editor
 * with process_id, every task links to a process
 * which is executed if this task is run
 */
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

