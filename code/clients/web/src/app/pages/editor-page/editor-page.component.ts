import { Component, OnInit, Input } from '@angular/core';
import { ProcessService } from 'app/services/process.service';
import { Observable } from 'rxjs/Observable';
import { Process } from 'app/models/Process';

@Component({
  selector: 'app-editor-page',
  templateUrl: './editor-page.component.html',
  styleUrls: ['./editor-page.component.scss']
})
export class EditorPageComponent implements OnInit {

  constructor(public processService: ProcessService) { }


  public processes: Observable<Process[]>;

  @Input()
  public showProcessList = true;

  ngOnInit() {
    this.processes = this.processService.all();
  }

  public toggleProcessList() {
    this.showProcessList = !this.showProcessList;
  }

}
