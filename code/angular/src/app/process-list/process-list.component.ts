import { Component, OnInit } from '@angular/core';
import { ProcessService } from 'app/services/process.service';
import { Observable } from 'rxjs/Observable';
import { Process } from 'app/models/Process';
import { ProcessParameterType } from 'app/models/ProcessParameter';

@Component({
  selector: 'app-process-list',
  templateUrl: './process-list.component.html',
  styleUrls: ['./process-list.component.scss']
})
export class ProcessListComponent implements OnInit {

  public processes: Process[];

  constructor(private processService: ProcessService) { }

  private createMock() {
    for (let x = 0; x < 30; x++) {

      const inputs = [];
      const outputs = [];

      for (let i = 0; i <= Math.round(Math.random() * 3); i++) {
        inputs.push({
          id: i,
          role: 'input',
          type: Math.round(Math.random() * 2),
          title: 'input' + i,
          abstract: 'This is input' + i,
          min_occurs: 1,
          max_occurs: 1,
        });
      }

      for (let i = 0; i <= Math.random() * 3; i++) {
        outputs.push({
          id: i,
          role: 'output',
          type: Math.round(Math.random() * 2),
          title: 'output' + i,
          abstract: 'This is output' + i,
          min_occurs: 1,
          max_occurs: 1,
        });
      }



      this.processService.create({
        id: x,
        title: 'Process' + x,
        abstract: 'This describes process' + x,
        identifier: 'process.' + x,
        inputs,
        outputs
      });
    }
  }

  async ngOnInit() {
    this.processes = await this.processService.all();
  }

}
