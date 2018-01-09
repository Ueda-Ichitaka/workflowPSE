export enum ProcessParameterType {
    LITERAL,
    COMPLEX,
    BOUNDING_BOX
}

export interface ProcessParameter<T extends 'input' | 'output'> {
    id: number;
    role: T;
    type: ProcessParameterType;
    title: string;
    abstract: string;
    min_occurs: number;
    max_occurs: number;
}
