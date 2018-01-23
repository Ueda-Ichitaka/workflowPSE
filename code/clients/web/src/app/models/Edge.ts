/**
 * connect two tasks with each other, the end points
 * are fixed to a specific input/output
 */
export interface Edge {
    id: number;
    a_id: number;
    b_id: number;
    input_id: number;
    output_id: number;
}
