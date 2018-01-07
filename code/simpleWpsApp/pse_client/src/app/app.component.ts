import { Component, OnInit, ViewChild } from '@angular/core';
import { ApiService } from 'app/api.service';
import { Observable } from 'rxjs/Observable';
import { EditorComponent } from 'app/editor/editor.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  title = 'app';

  @ViewChild('editor')
  editor: EditorComponent;


  processes: Observable<any[]>;
  constructor(private api: ApiService) {
    this.processes = api.getProcesses();
  }

  ngOnInit(): void {

  }

  addProcess(p) {
    this.editor.add(p);
  }
}
