import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { Process } from '../models/Process';
import { ProcessParameterType } from '../models/ProcessParameter';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { of } from 'rxjs/observable/of';
import { Subscriber } from 'rxjs/Subscriber';

@Injectable()
export class ProcessService {


  // ------------- START TEST DATA ---------------
  // Todo: Remove hard coded test data, add http support when server is ready.
  private testData: Process[] = [
    {
      id: 1, title: 'Process A', abstract: 'this is process A', identifier: 'process.a',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [], outputs: []
    },
    {
      id: 2, title: 'Process B', abstract: 'this is process B', identifier: 'process.b',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [], outputs: []
    },
    {
      id: 3, title: 'Process C', abstract: 'this is process C', identifier: 'process.c',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [], outputs: []
    },
    {
      id: 4, title: 'Process D', abstract: 'this is process D', identifier: 'process.d',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [
        { id: 0, role: 'input', type: 0, title: 'IO 0', abstract: '', min_occurs: 1, max_occurs: 1 },
      ], outputs: [
        { id: 1, role: 'output', type: 0, title: 'IO 1', abstract: '', min_occurs: 1, max_occurs: 1 },
      ]
    },
    {
      id: 5, title: 'Process E', abstract: 'this is process E', identifier: 'process.e',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [
        { id: 2, role: 'input', type: 1, title: 'IO 2', abstract: '', min_occurs: 1, max_occurs: 1 },
      ], outputs: [
        { id: 3, role: 'output', type: 1, title: 'IO 3', abstract: '', min_occurs: 1, max_occurs: 1 },
      ]
    },
    {
      id: 6, title: 'Process F', abstract: 'this is process F', identifier: 'process.f',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [
        { id: 4, role: 'input', type: 2, title: 'IO 4', abstract: '', min_occurs: 1, max_occurs: 1 },
      ], outputs: [
        { id: 5, role: 'output', type: 2, title: 'IO 5', abstract: '', min_occurs: 1, max_occurs: 1 },
      ]
    },
    {
      id: 7, title: 'Process G', abstract: 'this is process G', identifier: 'process.g',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [
        { id: 6, role: 'input', type: 0, title: 'IO 6', abstract: '', min_occurs: 1, max_occurs: 1 },
        { id: 7, role: 'input', type: 0, title: 'IO 7', abstract: '', min_occurs: 1, max_occurs: 1 },
      ], outputs: [
        { id: 8, role: 'output', type: 0, title: 'IO 8', abstract: '', min_occurs: 1, max_occurs: 1 },
      ]
    },
    {
      id: 8, title: 'Process H', abstract: 'this is process H', identifier: 'process.h',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [
        { id: 9, role: 'input', type: 0, title: 'IO 9', abstract: '', min_occurs: 1, max_occurs: 1 },
      ], outputs: [
        { id: 10, role: 'output', type: 0, title: 'IO 10', abstract: '', min_occurs: 1, max_occurs: 1 },
        { id: 11, role: 'output', type: 0, title: 'IO 11', abstract: '', min_occurs: 1, max_occurs: 1 },
      ]
    },
    {
      id: 9, title: 'Process I', abstract: 'this is process I', identifier: 'process.i',
      wps_id: 0, created_at: 0, updated_at: 0, inputs: [], outputs: []
    }
  ];

  // ------------- END TEST DATA ---------------


  private testObservable: Observable<Process[]>;
  private testSubscriber: Subscriber<Process[]>;

  constructor(private http: HttpClient) {
    // Create test observable
    this.testObservable = new Observable(subscriber => {
      // Create test subscriber to update the observable later (in the creat method)
      this.testSubscriber = subscriber;
      subscriber.next(this.testData);
    });
  }

  public all(): Observable<Process[]> {
    return this.testObservable;
  }

  public get(id: number): Observable<Process> {
    return this.testObservable.pipe(
      // Map Process[] to Process by findeing the right id
      map(data => data.find(process => process.id === id))
    );
  }

  public create(process: Partial<Process>): Observable<Process> {
    // Assign random id to process
    process.id = Math.round(Math.random() * 10000000);

    // Add new Process to Process list
    this.testData.push(<Process>process);

    // Update subscriber
    this.testSubscriber.next(this.testData);

    // Return created process
    return this.get(process.id);
  }

  public update(id: number, process: Partial<Process>): Observable<Process> {
    // Find process by id
    const result = this.testData.find(p => p.id === id);

    // Update process
    Object.assign(process, result);

    // Update observable
    this.testSubscriber.next(this.testData);

    // Return updated process
    return this.get(id);
  }

  public async remove(id: number): Promise<boolean> {
    // Find index by process id
    const index = this.testData.findIndex(p => p.id === id);

    // Remove from array
    this.testData.splice(index, 1);

    // Update observable
    this.testSubscriber.next(this.testData);

    return true;
  }
}
