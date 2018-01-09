import { ProcessParameter } from 'app/models/ProcessParameter';

export interface Process {
    id: number;
    title: string;
    abstract: string;
    identifier: string;
    inputs: ProcessParameter<'input'>[];
    outputs: ProcessParameter<'output'>[];
}
