import { Injectable } from '@angular/core';
import { Workflow } from '../models/Workflow';
import { Edge } from '../models/Edge';
import { Task, TaskState } from '../models/Task';
import { Artefact } from '../models/Artefact';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { of } from 'rxjs/observable/of';
import { Subscriber } from 'rxjs/Subscriber';

// tslint:disable-next-line:max-line-length
// tslint:disable-next-line:no-unused-expression
const w3 = `{"id":3,"title":"3 Workflow","edges":[{"id":-1,"a_id":2844,"b_id":141,"input_id":2,"output_id":1},{"id":-1,"a_id":5433,"b_id":141,"input_id":2,"output_id":5},{"id":-1,"a_id":141,"b_id":3515,"input_id":7,"output_id":3},{"id":-1,"a_id":2844,"b_id":3515,"input_id":6,"output_id":1},{"id":-1,"a_id":3515,"b_id":3974,"input_id":9,"output_id":8},{"id":-1,"a_id":3974,"b_id":7502,"input_id":4,"output_id":10},{"id":-1,"a_id":3974,"b_id":2269,"input_id":2,"output_id":11},{"id":-1,"a_id":7502,"b_id":3026,"input_id":6,"output_id":5},{"id":-1,"a_id":2269,"b_id":3026,"input_id":7,"output_id":3}],"tasks":[{"id":6230,"x":224,"y":48,"state":0,"process_id":1,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156453248,"updated_at":1516156453248},{"id":8049,"x":475,"y":47,"state":0,"process_id":2,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156455004,"updated_at":1516156455004},{"id":2098,"x":718,"y":48,"state":0,"process_id":3,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156457022,"updated_at":1516156457022},{"id":2844,"x":217,"y":144,"state":0,"process_id":4,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156463665,"updated_at":1516156463665},{"id":141,"x":534,"y":248,"state":0,"process_id":5,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156466725,"updated_at":1516156466725},{"id":5433,"x":493,"y":143,"state":0,"process_id":6,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156472462,"updated_at":1516156472462},{"id":3515,"x":342,"y":406,"state":0,"process_id":7,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156479425,"updated_at":1516156479425},{"id":3974,"x":638,"y":407,"state":0,"process_id":8,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156488852,"updated_at":1516156488852},{"id":7502,"x":611,"y":531,"state":0,"process_id":6,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156497198,"updated_at":1516156497198},{"id":2269,"x":868,"y":530,"state":0,"process_id":5,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156499193,"updated_at":1516156499193},{"id":3026,"x":797,"y":644,"state":0,"process_id":7,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156504789,"updated_at":1516156504789}],"creator_id":-1,"shared":false,"created_at":-1,"updated_at":-1}`;

// tslint:disable-next-line:max-line-length
// tslint:disable-next-line:no-unused-expression
const w4 = `{"id":4,"title":"WPS flow workflow","edges":[{"id":-1,"a_id":4823,"b_id":3431,"input_id":0,"output_id":1},{"id":-1,"a_id":4814,"b_id":3431,"input_id":0,"output_id":1},{"id":-1,"a_id":3431,"b_id":1991,"input_id":6,"output_id":1},{"id":-1,"a_id":4814,"b_id":1991,"input_id":7,"output_id":1},{"id":-1,"a_id":1991,"b_id":1401,"input_id":9,"output_id":8},{"id":-1,"a_id":1401,"b_id":9390,"input_id":7,"output_id":11},{"id":-1,"a_id":1401,"b_id":9390,"input_id":6,"output_id":10},{"id":-1,"a_id":9390,"b_id":3999,"input_id":0,"output_id":8},{"id":-1,"a_id":9390,"b_id":9797,"input_id":6,"output_id":8},{"id":-1,"a_id":1991,"b_id":9797,"input_id":7,"output_id":8}],"tasks":[{"id":4823,"x":70,"y":67,"state":0,"process_id":4,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156645936,"updated_at":1516156645936},{"id":4814,"x":330,"y":66,"state":0,"process_id":4,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156647505,"updated_at":1516156647505},{"id":3431,"x":153,"y":203,"state":0,"process_id":4,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156649444,"updated_at":1516156649444},{"id":1991,"x":433,"y":310,"state":0,"process_id":7,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156651150,"updated_at":1516156651150},{"id":1401,"x":202,"y":431,"state":0,"process_id":8,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156666190,"updated_at":1516156666190},{"id":9390,"x":376,"y":522,"state":0,"process_id":7,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156671284,"updated_at":1516156671284},{"id":3999,"x":238,"y":696,"state":0,"process_id":4,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156687014,"updated_at":1516156687014},{"id":9797,"x":655,"y":629,"state":0,"process_id":7,"input_artefacts":[],"ouput_artefacts":[],"created_at":1516156694334,"updated_at":1516156694334}],"creator_id":-1,"shared":false,"created_at":-1,"updated_at":-1}`;


export enum WorkflowValidationResult {
  ERROR,
  SUCCESSFUL,
  TITLE_TO_LONG,
  TITLE_TO_SHORT,
  // TODO: @David Add additional results
}

@Injectable()
export class WorkflowService {

  /**
   * ----------START TEST DATA----------
   * Todo: Remove hard coded test data, and add http support when server is ready.
   */

  private mockEdges: Edge[] = [
    { id: 1, a_id: 1, b_id: 2, input_id: 1, output_id: 1 },
    { id: 2, a_id: 1, b_id: 3, input_id: 1, output_id: 2 },
    { id: 3, a_id: 2, b_id: 4, input_id: 1, output_id: 1 },
    { id: 4, a_id: 3, b_id: 5, input_id: 1, output_id: 1 },
    { id: 5, a_id: 3, b_id: 6, input_id: 1, output_id: 2 },
    { id: 6, a_id: 4, b_id: 7, input_id: 1, output_id: 1 },
    { id: 7, a_id: 5, b_id: 7, input_id: 2, output_id: 1 }
  ];

  private mockInputArtefacts: Artefact<'input'>[] = [
    { parameter_id: 1, task_id: 1, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS1', created_at: 0, updated_at: 0 },
    { parameter_id: 4, task_id: 2, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS4', created_at: 0, updated_at: 0 },
    { parameter_id: 5, task_id: 3, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS5', created_at: 0, updated_at: 0 },
    { parameter_id: 8, task_id: 4, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS8', created_at: 0, updated_at: 0 },
    { parameter_id: 10, task_id: 5, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS10', created_at: 0, updated_at: 0 },
    { parameter_id: 12, task_id: 6, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS12', created_at: 0, updated_at: 0 },
    { parameter_id: 14, task_id: 7, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS14', created_at: 0, updated_at: 0 },
    { parameter_id: 15, task_id: 7, workflow_id: 1, role: 'input', format: 'literal', data: 'HelloWPS15', created_at: 0, updated_at: 0 }
  ];

  private mockOutputArtefacts: Artefact<'output'>[] = [
    { parameter_id: 2, task_id: 1, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS2', created_at: 0, updated_at: 0 },
    { parameter_id: 3, task_id: 1, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS3', created_at: 0, updated_at: 0 },
    { parameter_id: 6, task_id: 3, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS6', created_at: 0, updated_at: 0 },
    { parameter_id: 7, task_id: 3, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS7', created_at: 0, updated_at: 0 },
    { parameter_id: 9, task_id: 4, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS9', created_at: 0, updated_at: 0 },
    { parameter_id: 11, task_id: 5, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS11', created_at: 0, updated_at: 0 },
    { parameter_id: 13, task_id: 6, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS13', created_at: 0, updated_at: 0 },
    { parameter_id: 16, task_id: 7, workflow_id: 1, role: 'output', format: 'literal', data: 'HelloWPS16', created_at: 0, updated_at: 0 }
  ];

  private mockTasks: Task[] = [
    {
      id: 1, x: 100, y: 100, state: TaskState.READY, process_id: 1, input_artefacts: [this.mockInputArtefacts[0]],
      ouput_artefacts: [this.mockOutputArtefacts[0], this.mockOutputArtefacts[1]], created_at: 0, updated_at: 0
    },
    {
      id: 2, x: 350, y: 100, state: TaskState.WAITING, process_id: 2, input_artefacts: [this.mockInputArtefacts[1]],
      ouput_artefacts: [this.mockOutputArtefacts[2]], created_at: 0, updated_at: 0
    },
    {
      id: 3, x: 650, y: 100, state: TaskState.WAITING, process_id: 3, input_artefacts: [this.mockInputArtefacts[3]],
      ouput_artefacts: [this.mockOutputArtefacts[3], this.mockOutputArtefacts[4]], created_at: 0, updated_at: 0
    },
    {
      id: 4, x: 200, y: 300, state: TaskState.WAITING, process_id: 4, input_artefacts: [this.mockInputArtefacts[4]],
      ouput_artefacts: [this.mockOutputArtefacts[5]], created_at: 0, updated_at: 0
    },
    {
      id: 5, x: 450, y: 300, state: TaskState.WAITING, process_id: 5, input_artefacts: [this.mockInputArtefacts[5]],
      ouput_artefacts: [this.mockOutputArtefacts[6]], created_at: 0, updated_at: 0
    },
    {
      id: 6, x: 700, y: 300, state: TaskState.WAITING, process_id: 6, input_artefacts: [this.mockInputArtefacts[6]],
      ouput_artefacts: [this.mockOutputArtefacts[7]], created_at: 0, updated_at: 0
    },
    {
      id: 7, x: 300, y: 400, state: TaskState.WAITING, process_id: 7,
      input_artefacts: [this.mockInputArtefacts[7], this.mockInputArtefacts[8]],
      ouput_artefacts: [this.mockOutputArtefacts[8]], created_at: 0, updated_at: 0
    },
  ];


  private testData: Workflow[] = [
    { id: 1, title: 'Workflow A', edges: this.mockEdges, tasks: this.mockTasks, creator_id: 0, shared: true, created_at: 0, updated_at: 0 },
    { id: 2, title: 'Workflow B', edges: [], tasks: [], creator_id: 1, shared: false, created_at: 0, updated_at: 0 },
  ];

  /**
   * ----------END TEST DATA----------
   */

  private testObservable: Observable<Workflow[]>;
  private testSubscriber: Subscriber<Workflow[]>;

  constructor(private http: HttpClient) {
    this.testData.push(JSON.parse(w3));
    this.testData.push(JSON.parse(w4));

    // Create test observable
    this.testObservable = new Observable(subscriber => {
      // Create test subscriber to update the observable later (in the create method)
      this.testSubscriber = subscriber;
      subscriber.next(this.testData);
    });
  }

  public all(): Observable<Workflow[]> {
    return this.testObservable;
  }

  public get(id: number): Observable<Workflow> {
    return this.testObservable.pipe(
      // Map Process[] to Process by findeing the right id
      map(data => data.find(workflow => workflow.id === id))
    );
  }

  public create(workflow: Partial<Workflow>): Observable<Workflow> {
    // Assign random id to workflow
    workflow.id = Math.round(Math.random() * 10000000);

    // Add new Workflow to Workflow list
    this.testData.push(<Workflow>workflow);

    // Update subscriber
    this.testSubscriber.next(this.testData);

    // Return created workflow
    return this.get(workflow.id);
  }

  public update(id: number, workflow: Partial<Workflow>): Observable<Workflow> {
    // Find workflow by id
    const result = this.testData.find(p => p.id === id);

    // Update workflow
    Object.assign(workflow, result);

    // Update observable
    this.testSubscriber.next(this.testData);

    // Return updated workflow
    return this.get(id);
  }

  public async remove(id: number): Promise<boolean> {
    // Find index by workflow id
    const index = this.testData.findIndex(workflow => workflow.id === id);

    // Remove from array
    this.testData.splice(index, 1);

    // Update observable
    this.testSubscriber.next(this.testData);

    return true;
  }

  // TODO: @David Validate workflow
  public validate(workflow: Workflow): WorkflowValidationResult {

    // check name
    if (workflow.title.length > 255) {
      return WorkflowValidationResult.TITLE_TO_LONG;
    } else if (workflow.title.length < 1) {
      return WorkflowValidationResult.TITLE_TO_SHORT;
    }

    // TODO: @David add additional checks
    // - cycle check

    return WorkflowValidationResult.SUCCESSFUL;
  }
}
