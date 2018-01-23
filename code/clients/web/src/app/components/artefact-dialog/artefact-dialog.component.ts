import { Component, OnInit, Inject, ViewEncapsulation, ViewChild, ElementRef } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material';
import { ProcessParameter, ProcessParameterType } from 'app/models/ProcessParameter';
import { ProcessService } from 'app/services/process.service';
import { Process } from 'app/models/Process';
import { Task } from 'app/models/Task';
import { TaskComponent } from 'app/components/task/task.component';
import { analyzeFile } from '@angular/compiler';

interface ArtefactDialogData {
  task: TaskComponent;
  parameter: ProcessParameter<'input' | 'output'>;
}

declare var hljs: any;
@Component({
  selector: 'app-artefact-dialog',
  templateUrl: './artefact-dialog.component.html',
  styleUrls: ['./artefact-dialog.component.scss'],
})
export class ArtefactDialogComponent implements OnInit {

  public selectedFormat = 'markdown';
  public data: any = {};

  public editMode = true;

  public task: TaskComponent;
  public parameter: ProcessParameter<'input' | 'output'>;

  constructor( @Inject(MAT_DIALOG_DATA) data: ArtefactDialogData, public dialog: MatDialogRef<ArtefactDialogComponent>) {
    this.task = data.task;
    this.parameter = data.parameter;
  }

  @ViewChild('code')
  public codeComponent: ElementRef;

  public ngOnInit() {
  }

  public getTypeInfo(type: number): [string, string] {
    return [ProcessService.getTypeName(type), ProcessService.getTypeColor(type)];
  }

  public clickEditButton() {
    const el: HTMLElement = this.codeComponent.nativeElement;

    if (this.editMode) {
      el.className = '';
      el.innerHTML = '';

      const format = this.parameter.type === ProcessParameterType.COMPLEX
        ? this.selectedFormat
        : 'markdown';

      el.classList.add(format);

      const data = this.parameter.type === ProcessParameterType.BOUNDING_BOX
        ? `${this.data.tx}, ${this.data.ty}, ${this.data.bx}, ${this.data.by}`
        : this.data.value;

      el.appendChild(document.createTextNode(data));
    }

    setTimeout(() => { hljs.highlightBlock(el); }, 20);
    this.editMode = !this.editMode;
  }

  public save() {
    if (!this.data) {
      return;
    }

    const out = {
      value: this.data.value || `${this.data.tx},${this.data.ty},${this.data.bx},${this.data.by}`,
      format: this.selectedFormat === 'markdown' ? 'plain' : this.selectedFormat
    };

    if (out.value.length > 0) {
      this.task.addArtefact(this.parameter, out);
    }

    this.dialog.close();
  }
}
