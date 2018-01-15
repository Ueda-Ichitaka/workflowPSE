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

  public processes: Observable<Process[]>;

  constructor(private processService: ProcessService) { }

  async ngOnInit() {
    this.processes = this.processService.all();
  }

}
