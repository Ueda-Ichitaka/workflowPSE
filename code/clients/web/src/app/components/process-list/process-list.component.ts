import { Component, OnInit, Input, ChangeDetectionStrategy } from '@angular/core';
import { ProcessService } from 'app/services/process.service';
import { Observable } from 'rxjs/Observable';
import { Process } from 'app/models/Process';
import { ProcessParameterType } from 'app/models/ProcessParameter';
import { WPS } from 'app/models/WPS';


@Component({
  selector: 'app-process-list',
  templateUrl: './process-list.component.html',
  styleUrls: ['./process-list.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ProcessListComponent implements OnInit {

  @Input()
  private processes: Process[];

  @Input()
  public wps: WPS[];


  public constructor() { }

  public ngOnInit() {

  }

  public processByWPS(id: number) {
    return this.processes.filter(process => process.wps_id === id);
  }
}
