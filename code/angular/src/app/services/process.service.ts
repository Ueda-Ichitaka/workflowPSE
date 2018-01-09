import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { Process } from 'app/models/Process';
import { ProcessParameterType } from 'app/models/ProcessParameter';
import { catchError, map, tap, switchMap } from 'rxjs/operators';

@Injectable()
export class ProcessService {

  constructor(private http: HttpClient) {

  }

  public async all(): Promise<Process[]> {
    const data = await this.http.get<{ [key: string]: Process }>('https://wpsflow.firebaseio.com/processes.json').toPromise();
    return Object.values(data);
  }

  public async get(id: number): Promise<Process> {
    const a = await this.all();
    return a.find(p => p.id === id);
  }

  public async create(process: Partial<Process>): Promise<Process> {
    return <any>this.http.post('https://wpsflow.firebaseio.com/processes.json', process).toPromise();
  }

  public update(id: number, process: Partial<Process>): Promise<Process> {
    return null;
  }

  public remove(id: number): boolean {
    return null;
  }
}
