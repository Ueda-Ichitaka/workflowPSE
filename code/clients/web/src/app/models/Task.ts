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

<<<<<<< HEAD
=======
/**
 * tasks describe the actual task elements which are
 * displayed in the editor
 * with process_id, every task links to a process
 * which is executed if this task is run
 */
>>>>>>> 1033a8b42676f9a381f248a149d0e8c9d9b1525d
export interface Task {
    id: number;
    x: number;
    y: number;
    state: TaskState;
    process_id: number;
    input_artefacts: Artefact<'input'>[];
    output_artefacts: Artefact<'output'>[];
    created_at: number;
    updated_at: number;
}

