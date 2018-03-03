import { Edge } from 'app/models/Edge';
import { Task } from 'app/models/Task';

/**
 * a workflow contains all related
 * edges and tasks
 */
export interface Workflow {
    id: number;
    title: string;
    edges: Edge[];
    tasks: Task[];
    creator_id: number;
    shared: boolean;
    percent_done?: number;
    created_at: number;
    updated_at: number;
}
