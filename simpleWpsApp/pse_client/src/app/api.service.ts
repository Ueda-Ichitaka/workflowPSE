import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/of';
import { Http } from '@angular/http';

@Injectable()
export class ApiService {
    constructor(private http: Http) {

    }

    public getProcesses(): Observable<any[]> {
        return Observable.of([
            { identifier: 'say_hallo', input: [], output: ['out1'] },
            { identifier: 'say_das', input: ['in1'], output: ['out1'] },
            { identifier: 'say_ist', input: ['in1'], output: ['out1'] },
            { identifier: 'say_pse_projekt', input: ['in1'], output: ['out1'] },
            { identifier: 'say_und', input: ['in1', 'in2'], output: ['out1'] },
        ]);
    }
}
