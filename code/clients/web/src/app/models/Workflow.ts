import { Edge } from 'app/models/Edge';
import { Task } from 'app/models/Task';

export interface Workflow {
    id: number;
    title: string;
    edges: Edge[];
    tasks: Task[];
    creator_id: number;
    shared: boolean;
    created_at: number;
    updated_at: number;
}