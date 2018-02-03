import { Component, OnInit, Inject, ViewEncapsulation, ViewChild, ElementRef } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material';
import { ProcessParameter, ProcessParameterType } from 'app/models/ProcessParameter';
import { ProcessService } from 'app/services/process.service';
import { Process } from 'app/models/Process';
import { Task } from 'app/models/Task';
import { TaskComponent } from 'app/components/task/task.component';
import { analyzeFile } from '@angular/compiler';
import { Artefact } from 'app/models/Artefact';

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

  public deletable = false;

  /**
   * creates an artefact object
   * @param data the artefact data
   * @param dialog the artefact dialog
   */
  constructor( @Inject(MAT_DIALOG_DATA) data: ArtefactDialogData, public dialog: MatDialogRef<ArtefactDialogComponent>) {
    this.task = data.task;
    this.parameter = data.parameter;
    // Get all artefacts of this tasks
    const artefacts: Artefact<'input' | 'output'>[] = this.parameter.role === 'input'
      ? this.task.task.input_artefacts
      : this.task.task.output_artefacts;

    const artefact = artefacts.find(a => a.parameter_id === this.parameter.id);

    // Check if parameter has artefact
    if (artefact) {
      this.data = {
        value: artefact.data,
        format: artefact.format,
      };
    } else {
      this.data = {
        format: this.parameter.format || 'string',
      };
    }

    if (this.data.value) {
      this.deletable = true;
    }
  }

  @ViewChild('code')
  public codeComponent: ElementRef;

  public ngOnInit() {
  }

  public get valid(): boolean {
    // Check Literal Data
    if (this.parameter.type === ProcessParameterType.LITERAL) {
      if (!this.data.value || this.data.value.length === 0) {
        return false;
      }

      switch (this.data.format) {
        case 'string': return true;
        case 'float': return !isNaN(this.data.value);
        case 'integer': return /^-?[0-9]+$/.test(this.data.value);
        default: return true; /* Match any type */
      }
    }

    return true;
  }

  /**
   * @param type the type of the parameter
   * @returns the type as a string and the color of the artefact
   */
  public getTypeInfo(type: number): [string, string] {
    return [ProcessService.getTypeName(type), ProcessService.getTypeColor(type)];
  }

  /**
   * is used to change input of the different input types
   * as every input type requires different fields,
   * we have to differ between them
   */
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
        ? `UpperCorner=${this.data.tx} ${this.data.ty};LowerCorner=${this.data.bx} ${this.data.by}`
        : this.data.value;

      if (data) {
        el.appendChild(document.createTextNode(data));
      }

    }

    setTimeout(() => { hljs.highlightBlock(el); }, 20);
    this.editMode = !this.editMode;
  }

  /**
   * saves the artefacts modified input
   */
  public save() {
    if (!this.data) {
      return;
    }

    const out = {
      value: this.parameter.type === ProcessParameterType.BOUNDING_BOX
        ? `UpperCorner=${this.data.tx} ${this.data.ty};LowerCorner=${this.data.bx} ${this.data.by}`
        : this.data.value,

      format: this.selectedFormat === 'markdown' ? 'plain' : this.selectedFormat
    };

    if (out.value && out.value.length > 0) {
      this.task.addArtefact(this.parameter, out);
    }

    this.dialog.close();
  }

  public remove() {
    this.task.removeArtefact(this.parameter);
    this.dialog.close();
  }
}
