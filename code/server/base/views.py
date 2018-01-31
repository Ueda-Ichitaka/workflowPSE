import calendar
import datetime
import json

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, View

from base import cron, utils
from base.models import InputOutput, WPSProvider, Process, Artefact, Edge, Task, Workflow, WPS


# TODO: tests, documentation
def as_json_response(list):
    """

    @param list:
    @type list:
    @return:
    @rtype:
    """
    return JsonResponse(list, safe=False)


class IndexView(TemplateView):
    template_name = "base/index.html"


# TODO: tests, documentation
class UserView(View):
    """

    """

    @staticmethod
    @require_GET
    def index(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        # TODO: Was not tested yet because of absence of user management in our project now
        return as_json_response(model_to_dict(request.user))


# TODO: tests, documentation
class WorkflowView(View):
    """

    """

    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """

        @param args:
        @type args:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return super(WorkflowView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        if 'workflow_id' in kwargs:
            workflow = get_object_or_404(Workflow, pk=kwargs['workflow_id'])

            # get_object_or_404() ist not used here because for some reason
            # it does not include created_at and updated_at fields
            returned = list(Workflow.objects.filter(pk=kwargs['workflow_id']).values())[0]

            returned['title'] = returned['name']
            returned['created_at'] = calendar.timegm(returned['created_at'].timetuple())
            returned['updated_at'] = calendar.timegm(returned['updated_at'].timetuple())

            returned['edges'] = list(workflow.edge_set.all().values())
            tasks = list(workflow.task_set.all().values())

            for (i, task) in enumerate(tasks):
                tasks[i]['state'] = int(tasks[i]['status'])
                tasks[i]['x'] = float(task['x'])
                tasks[i]['y'] = float(task['y'])

                if task['started_at'] is not None:
                    tasks[i]['started_at'] = calendar.timegm(task['started_at'].timetuple())

                input_artefacts = list(Artefact.objects.filter(task=task['id']).filter(role=0).values())
                output_artefacts = list(Artefact.objects.filter(task=task['id']).filter(role=1).values())

                for (j, input_artefact) in enumerate(input_artefacts):
                    input_artefacts[j]['created_at'] = calendar.timegm(input_artefact['created_at'].timetuple())
                    input_artefacts[j]['updated_at'] = calendar.timegm(input_artefact['updated_at'].timetuple())

                for (j, output_artefact) in enumerate(output_artefacts):
                    output_artefacts[j]['created_at'] = calendar.timegm(output_artefact['created_at'].timetuple())
                    output_artefacts[j]['updated_at'] = calendar.timegm(output_artefact['updated_at'].timetuple())

                tasks[i]['input_artefacts'] = input_artefacts
                tasks[i]['output_artefacts'] = output_artefacts

            returned['tasks'] = tasks

            return as_json_response(returned)
        else:
            returned = list(Workflow.objects.all().values())

            for (i, workflow) in enumerate(returned):
                returned[i]['title'] = workflow['name']
                returned[i]['created_at'] = calendar.timegm(workflow['created_at'].timetuple())
                returned[i]['updated_at'] = calendar.timegm(workflow['updated_at'].timetuple())

                returned[i]['edges'] = list(Edge.objects.filter(workflow=workflow['id']).values())
                tasks = list(Task.objects.filter(workflow=workflow['id']).values())

                for (j, task) in enumerate(tasks):
                    tasks[j]['state'] = int(task['status'])
                    tasks[j]['x'] = float(task['x'])
                    tasks[j]['y'] = float(task['y'])

                    if task['started_at'] is not None:
                        tasks[j]['started_at'] = calendar.timegm(task['started_at'].timetuple())

                    input_artefacts = list(Artefact.objects.filter(task=task['id']).filter(role=0).values())
                    output_artefacts = list(Artefact.objects.filter(task=task['id']).filter(role=1).values())

                    for (k, input_artefact) in enumerate(input_artefacts):
                        input_artefacts[k]['created_at'] = calendar.timegm(input_artefact['created_at'].timetuple())
                        input_artefacts[k]['updated_at'] = calendar.timegm(input_artefact['updated_at'].timetuple())

                    for (k, output_artefact) in enumerate(output_artefacts):
                        output_artefacts[k]['created_at'] = calendar.timegm(output_artefact['created_at'].timetuple())
                        output_artefacts[k]['updated_at'] = calendar.timegm(output_artefact['updated_at'].timetuple())

                    tasks[j]['input_artefacts'] = input_artefacts
                    tasks[j]['output_artefacts'] = output_artefacts

                returned[i]['tasks'] = tasks

            return as_json_response(returned)

    @staticmethod
    def post(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)

        new_workflow = Workflow.objects.create(
            name=new_data['title'],
            percent_done=0,
            creator_id=1,  # TODO: request.user.id
            last_modifier_id=1  # TODO: request.user.id
        )

        temporary_to_new_task_ids = {}

        for new_task_data in new_data['tasks']:
            new_task = Task.objects.create(
                workflow_id=new_workflow.id,
                process_id=new_task_data['process_id'],
                x=new_task_data['x'],
                y=new_task_data['y'],
                status=new_task_data['state']
            )

            temporary_to_new_task_ids[new_task_data['id']] = new_task.id

            artefacts_data = new_task_data['input_artefacts'] + new_task_data['output_artefacts']

            for artefact_data in artefacts_data:
                Artefact.objects.create(
                    task_id=new_task.id,
                    parameter_id=artefact_data['parameter_id'],
                    role=(0 if artefact_data['role'] == 'input' else 1),
                    format=artefact_data['format'],
                    data=artefact_data['data']
                )

        for new_edge_data in new_data['edges']:
            Edge.objects.create(
                workflow_id=new_workflow.id,
                from_task_id=temporary_to_new_task_ids[new_edge_data['from_task_id']],
                to_task_id=temporary_to_new_task_ids[new_edge_data['to_task_id']],
                input_id=new_edge_data['input_id'],
                output_id=new_edge_data['output_id']
            )

        return WorkflowView.get(request, workflow_id=new_workflow.id)

    @staticmethod
    def patch(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)
        workflow = get_object_or_404(Workflow, pk=kwargs['workflow_id'])

        workflow.name = new_data['title']
        workflow.last_modifier_id = 1  # TODO: request.user.id

        workflow.save()

        temporary_to_new_task_ids = {}

        for task_data in new_data['tasks']:
            if task_data['id'] > 0:
                task = get_object_or_404(Task, pk=task_data['id'])

                task.workflow_id = workflow.id
                task.process_id = task_data['process_id']
                task.x = task_data['x']
                task.y = task_data['y']
                task.status = task_data['state']

                task.save()

                artefacts_data = task_data['input_artefacts'] + task_data['output_artefacts']

                for artefact_data in artefacts_data:
                    if ('id' in artefact_data) and (artefact_data['id'] > 0):
                        artefact = get_object_or_404(Artefact, pk=artefact_data['id'])

                        artefact.task_id = task.id
                        artefact.parameter_id = artefact_data['parameter_id']
                        artefact.role = (0 if artefact_data['role'] == 'input' else 1)
                        artefact.format = artefact_data['format']
                        artefact.data = artefact_data['data']

                        artefact.save()
                    else:
                        Artefact.objects.create(
                            task_id=task.id,
                            parameter_id=artefact_data['parameter_id'],
                            role=(0 if artefact_data['role'] == 'input' else 1),
                            format=artefact_data['format'],
                            data=artefact_data['data']
                        )
            else:
                task = Task.objects.create(
                    workflow_id=workflow.id,
                    process_id=task_data['process_id'],
                    x=task_data['x'],
                    y=task_data['y'],
                    status=task_data['state']
                )

            temporary_to_new_task_ids[task_data['id']] = task.id

        for edge_data in new_data['edges']:
            if edge_data['id'] > 0:
                edge = get_object_or_404(Edge, pk=edge_data['id'])

                edge.workflow = workflow
                edge.from_task_id = temporary_to_new_task_ids[edge_data['from_task_id']]
                edge.to_task_id = temporary_to_new_task_ids[edge_data['to_task_id']]
                edge.input_id = edge_data['input_id']
                edge.output_id = edge_data['output_id']

                edge.save()
            else:
                Edge.objects.create(
                    workflow_id=workflow.id,
                    from_task_id=temporary_to_new_task_ids[edge_data['from_task_id']],
                    to_task_id=temporary_to_new_task_ids[edge_data['to_task_id']],
                    input_id=edge_data['input_id'],
                    output_id=edge_data['output_id']
                )

        return WorkflowView.get(request, workflow_id=kwargs['workflow_id'])

    @staticmethod
    def delete(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        workflow = get_object_or_404(Workflow, pk=kwargs['workflow_id'])
        (deletedWorkflowCount, countOfDeletionsPerType) = workflow.delete()
        deleted = (deletedWorkflowCount > 0)

        return JsonResponse({'deleted': deleted})

    @staticmethod
    @require_GET
    def start(request, workflow_id):
        """

        @param request:
        @type request:
        @param workflow_id:
        @type workflow_id:
        @return:
        @rtype:
        """
        Task.objects.filter(workflow=workflow_id).update(status=1)

        # TODO: return {"error": "..."} for some errors
        return JsonResponse({})

    @staticmethod
    @require_GET
    def stop(request, workflow_id):
        """

        @param request:
        @type request:
        @param workflow_id:
        @type workflow_id:
        @return:
        @rtype:
        """
        Task.objects.filter(workflow=workflow_id).update(status=0)

        return JsonResponse({})


# TODO: tests, documentation
class ProcessView(View):
    """

    """

    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """

        @param args:
        @type args:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return super(ProcessView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        if 'process_id' in kwargs:
            process = Process.objects.get(pk=kwargs['process_id'])
            returned = model_to_dict(process)
            inputs = list(process.inputoutput_set.all().filter(role=0).values())
            outputs = list(process.inputoutput_set.all().filter(role=1).values())

            for (j, input) in enumerate(inputs):
                inputs[j]['type'] = int(input['datatype'])
                inputs[j]['role'] = ('input' if input['role'] == '0' else 'output')

            for (j, output) in enumerate(outputs):
                outputs[j]['type'] = int(output['datatype'])
                outputs[j]['role'] = ('input' if output['role'] == '0' else 'output')

            returned['inputs'] = inputs
            returned['outputs'] = outputs

            return as_json_response(returned)
        else:
            returned = list(Process.objects.all().values())

            for (i, process) in enumerate(returned):
                inputs = list(InputOutput.objects.filter(process=process['id']).filter(role=0).values())
                outputs = list(InputOutput.objects.filter(process=process['id']).filter(role=1).values())

                for (j, input) in enumerate(inputs):
                    inputs[j]['type'] = int(input['datatype'])
                    inputs[j]['role'] = ('input' if input['role'] == '0' else 'output')

                for (j, output) in enumerate(outputs):
                    outputs[j]['type'] = int(output['datatype'])
                    outputs[j]['role'] = ('input' if output['role'] == '0' else 'output')

                returned[i]['inputs'] = inputs
                returned[i]['outputs'] = outputs

            return as_json_response(returned)

    @staticmethod
    def post(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        return JsonResponse({'error': 'this REST interface is not supported'})

    @staticmethod
    def patch(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return JsonResponse({'error': 'this REST interface is not supported'})

    @staticmethod
    def delete(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return JsonResponse({'error': 'this REST interface is not supported'})


# TODO: tests, documentation
class WPSView(View):
    """

    """

    # needed because Django needs CSRF token in cookie unless you put this
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """

        @param args:
        @type args:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        return super(WPSView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        if 'wps_id' in kwargs:
            wps = WPS.objects.get(pk=kwargs['wps_id'])
            returned = model_to_dict(wps)
            returned['provider'] = model_to_dict(wps.service_provider)
            returned['provider']['title'] = returned['provider']['provider_name']
            returned['provider']['site'] = returned['provider']['provider_site']
            return as_json_response(returned)
        else:
            returned = list(WPS.objects.all().values())

            for (i, wps) in enumerate(returned):
                returned[i]['provider'] = model_to_dict(WPSProvider.objects.get(pk=wps['service_provider_id']))
                returned[i]['provider']['title'] = returned[i]['provider']['provider_name']
                returned[i]['provider']['site'] = returned[i]['provider']['provider_site']

            return as_json_response(returned)

    @staticmethod
    def post(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        utils.add_wps_server(request.body.decode('utf-8'))

        return JsonResponse({})

    @staticmethod
    def patch(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        new_data = json.loads(request.body)
        wps = get_object_or_404(WPS, pk=kwargs['wps_id'])

        if new_data['provider']['id'] > 0:
            wps_provider = get_object_or_404(WPSProvider, pk=new_data['provider']['id'])

            wps_provider.provider_name = new_data['provider']['title']
            wps_provider.provider_site = new_data['provider']['site']

            wps_provider.save()

            wps_provider_id = new_data['provider']['id']
        else:
            new_wps_provider = WPSProvider.objects.create(
                provider_name=new_data['provider']['title'],
                provider_site=new_data['provider']['url']
            )

            wps_provider_id = new_wps_provider.id

        wps.service_provider_id = wps_provider_id
        wps.title = new_data['title']
        wps.abstract = new_data['abstract']

        wps.save()

        return WPSView.get(request, wps_id=kwargs['wps_id'])

    @staticmethod
    def delete(request, **kwargs):
        """

        @param request:
        @type request:
        @param kwargs:
        @type kwargs:
        @return:
        @rtype:
        """
        wps = get_object_or_404(WPS, pk=kwargs['wps_id'])
        (deletedWPSCount, countOfDeletionsPerType) = wps.delete()
        deleted = (deletedWPSCount > 0)

        return JsonResponse({'deleted': deleted})

    @staticmethod
    @require_GET
    def refresh(request):
        """

        @param request:
        @type request:
        @return:
        @rtype:
        """
        cron.update_wps_processes()

        return JsonResponse({})


# TODO: tests, documentation
class WorkflowsView(TemplateView):
    """

    """
    template_name = "index.html"


# TODO: tests, documentation
class EditorView(TemplateView):
    """

    """
    template_name = "index.html"


# TODO: tests, documentation
class SettingsView(TemplateView):
    """

    """
    template_name = "index.html"
